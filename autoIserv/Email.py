from autoIserv.util import download_file_from_iserv

from datetime import datetime
from selenium.common.exceptions import TimeoutException, MoveTargetOutOfBoundsException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.webelement import FirefoxWebElement
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from urllib.parse import urljoin
import json
import base64
from os import path


class Email:

    def __init__(self):
        self.html_element = None
        self.index = None
        self.driver = None
        self.real_base_url = None

        self.seen = None
        self.by = None

        self.subject = None
        self.date = None

        self.size_unit = None
        self.size = None

        self.raw_text_content = None
        self.html_content = None
        self.attachments = {}


    def get_basic_data(self, html_element : FirefoxWebElement, index: int, web_driver : WebDriver, base_url : str):
        self.html_element = html_element
        self.index = index
        self.driver = web_driver
        self.real_base_url = base_url.split("/")[0]

        classes = html_element.get_attribute("class").split(" ")
        for css_class in classes:
            if css_class == "mail-row-unseen":
                self.seen = False
            elif css_class == "mail-row-seen":
                self.seen = True

        self.by = html_element.find_element_by_class_name("msg-from").text

        subject_elements = WebDriverWait(html_element, 5).until(EC.presence_of_all_elements_located((By.XPATH, "//td[contains(@class, 'msg-subject') and text() != '']")))

        self.subject = subject_elements[index].get_attribute("title")
        if self.subject == '':
            self.subject = subject_elements[index].text

        date_web_objects = WebDriverWait(html_element, 5).until(EC.presence_of_all_elements_located((By.XPATH, "//td[contains(@class, 'msg-date') and text() != '']")))
        self.date = datetime.strptime(date_web_objects[index].text, "%d.%m.%Y %H:%M")

        size_text = html_element.find_element_by_class_name("msg-size").text.lower()
        size_str, self.size_unit = size_text.split(" ")
        self.size = float(size_str.replace(",", ".").replace(" ", ""))

        self.raw_text_content = None
        self.html_content = None
        self.attachments = {}


    def view(self, download_attachments=True):
        print(f"[*] Viewing Email : '{self.subject}'")
        subject_elements = WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, "//td[contains(@class, 'msg-subject') and text() != '']")))
        try:
            ActionChains(self.driver).move_to_element(subject_elements[self.index]).perform()
        except MoveTargetOutOfBoundsException:
            pass
        subject_elements = WebDriverWait(self.driver, 5).until(
            EC.visibility_of_all_elements_located((By.XPATH, "//td[contains(@class, 'msg-subject') and text() != '']")))
        subject_elements[self.index].click()

        body = WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@id='message-body' and text() != '']")))

        message_content = body.find_element_by_id("message-content")
        self.raw_text_content = message_content.text

        try:
            WebDriverWait(self.driver, 4).until(EC.frame_to_be_available_and_switch_to_it((By.CLASS_NAME, "mail-iframe")))
            self.html_content = f'<div id="message-content"><div class="iframe-container">{self.driver.find_element_by_tag_name("body").get_attribute("innerHTML")}</div></div>'
            self.driver.switch_to.default_content()

        except TimeoutException:
            self.html_content = str(message_content.get_attribute('outerHTML').encode('utf-8'), encoding="utf-8")

        if download_attachments:
            message_attachments = body.find_element_by_id("message-attachments")
            attachments = message_attachments.find_elements_by_class_name("attachment")

            for i, attachment in enumerate(attachments):
                drop_down_button = attachment.find_element_by_tag_name("button")
                drop_down_button.click()

                drop_down_menu = attachment.find_element_by_class_name("dropdown-menu")

                download_link = WebDriverWait(drop_down_menu, 5).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, "attachment-download")))

                download_url = urljoin(self.real_base_url, download_link.get_attribute('href'))

                print(f"[*] Downloading Attachment : {download_url}")
                result = download_file_from_iserv(self.driver, download_url)
                if result:
                    print(f"[*] '{result[0]}' was downloaded")
                    self.attachments[result[0]] = result[1].content

        self.driver.find_element_by_id("mail-back").click()


    def __repr__(self):
        return f"<autoIserv.Email.Email (subject='{self.subject}' seen={self.seen} by='{self.by}' size={self.size}{self.size_unit} date={self.date})>"


    def save(self, email_dir, attachment_dir=None, store_attachments_in_file=True):
        data = {
            "Subject" : self.subject,
            "Seen" : self.seen,
            "By" : self.by,
            "Size" : {
                "Value" : self.size,
                "Unit" : self.size_unit
            },
            "Date" : self.date.strftime("%d.%m.%Y %H_%M"),
            "AttachmentNames" : []
        }

        if self.html_content:
            data["raw_html"] = self.html_content

        if self.raw_text_content:
            data["raw_text"] = self.raw_text_content

        if len(self.attachments) > 0:
            if store_attachments_in_file:
                data["Attachments"] = {}
            for attachment_name in self.attachments:
                attachment_content = self.attachments[attachment_name]
                data["AttachmentNames"].append(attachment_name)
                if store_attachments_in_file:
                    data["Attachments"][attachment_name]= str(base64.b64encode(attachment_content), encoding="utf-8")
                if attachment_dir:
                    if path.isdir(attachment_dir):
                        file_path = f"{attachment_dir}\\{attachment_name}"
                        print(f"[*] Saving Attachment to {file_path}")
                        file = open(file_path, mode="wb")
                        file.write(attachment_content)
                        file.close()

        email_path = f"{email_dir}\\" + f"{self.subject}-{self.date}-{self.size}{self.size_unit}_{self.index}.email-json".replace(":", "").replace("\\", "").replace("/", "").replace("?", "").replace("*", "").replace("<", "").replace(">", "").replace('"', "").replace("|", "")
        print(f"[*] Saving email to : {email_path}")
        with open(email_path, 'w', encoding="utf-8") as file:
            json.dump(data, file)


    def save_attachment_to_file(self, attachment, attachment_dir):
        file_path = f"{attachment_dir}\\{attachment_dir}"
        file = open(file_path, mode="wb")
        file.write(self.attachments[attachment])
        file.close()


    @staticmethod
    def load(path, store_attachments=True):
        data = json.load(open(path, mode="r", encoding="utf-8"))
        email = Email()
        email.subject = data["Subject"]
        email.seen = data["Seen"]
        email.by = data["By"]
        email.size = data["Size"]["Value"]
        email.size_unit = data["Size"]["Unit"]
        email.date = datetime.strptime(data["Date"], "%d.%m.%Y %H_%M")

        if store_attachments:
            try:
                for attachment in data["Attachments"]:
                    email.attachments[attachment] = base64.b64decode(data["Attachments"][attachment])
            except KeyError:
                pass

        if len(email.attachments) == 0:
            for name in data["AttachmentNames"]:
                email.attachments[name] = b""

        if data["raw_html"]:
            email.html_content = data["raw_html"]

        if data["raw_text"]:
            email.raw_text_content = data["raw_text"]

        return email