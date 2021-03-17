from autoIserv.util import download_file_from_iserv

from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.webelement import FirefoxWebElement
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from urllib.parse import urljoin
import os
import json


class Exercise:

    SUBJECT_KEYWORDS = {
        "Latin": ["Latein"],
        "France": ["Französisch"],
        "Spanish": ["Spanisch"],
        "Biology" : ["Biologie", "Bio"],
        "Physics": ["Physik"],
        "Chemistry": ["Chemie"],
        "Music" : ["Musik"],
        "Art" : ["Kunst"],
        "Computer Science" : ["Informatik"],
        "History": ["Geschichte", "Geschichtsaufgabe"],
        "Politics" : ["Politik", "Gesetze"],
        "English": ["Englisch", "English", "Unit"],
        "Math": ["Matheaufgaben", "Mathe", "Mathematik", "Berechne", "Berechnen"],
        "German": ["Deutsch", "Gedicht"],
    }

    def __init__(self):
        self.html_element = None
        self.index = None
        self.driver = None
        self.real_base_url = None

        # Basic Data
        self.title = None
        self.start_date = None
        self.due_date = None
        self.subject = None
        self.view_url = None
        self.tags = None

        # Advanced Data
        self.description = None
        self.by = None
        self.attachments = {}

        self.new = True

    def get_basic_data(self, html_element: FirefoxWebElement, index: int, web_driver: WebDriver, base_url: str):
        self.html_element = html_element
        self.index = index
        self.driver = web_driver
        self.real_base_url = base_url.split("/")[0]

        columns = html_element.find_elements_by_tag_name("td")
        for i, column in enumerate(columns):
            if i == 0:
                self.title = column.text
                try:
                    show_link_element = column.find_element_by_tag_name("a")
                    self.view_url = show_link_element.get_attribute("href")
                except NoSuchElementException:
                    return False
            elif i == 1:
                self.start_date = datetime.strptime(column.text, "%d.%m.%Y")
            elif i == 2:
                span_element = column.find_element_by_tag_name("span")
                due_date_data_string = span_element.get_attribute("data-date").split("+")[0]
                self.due_date = datetime.strptime(due_date_data_string, "%Y-%m-%dT%H:%M:%S")
            elif i == 3:
                tags_text = column.text
                if tags_text != "(keine)":
                    self.tags = str(column.text)
                    self.figure_out_subject_based_on_tags()
        return True


    def figure_out_subject(self):
        if self.subject != "not_found" and self.subject != None:
            return
        search_string = (str(self.title) + str(self.description)).lower()
        for subject in self.SUBJECT_KEYWORDS:
            for key_word in self.SUBJECT_KEYWORDS[subject]:
                if key_word.lower() in search_string:
                    self.subject = subject
                    return
        self.subject = "not_found"


    def figure_out_subject_based_on_tags(self):
        if self.tags:
            for subject in self.SUBJECT_KEYWORDS:
                for key_word in self.SUBJECT_KEYWORDS[subject]:
                    if key_word.lower() in self.tags.lower():
                        self.subject = subject
                        return
        self.subject = "not_found"


    def view(self, download_attachments=True):
        self.driver.get(self.view_url)
        print(f"[*] Viewing Exercise : '{self.title}'")
        site_content = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "page-content")))
        site_row = site_content.find_element_by_class_name("row")
        information_table = WebDriverWait(site_row, 3).until(EC.presence_of_element_located((By.XPATH, "div[1]/div/table/tbody")))
        information_rows = information_table.find_elements_by_tag_name("tr")

        for row in information_rows:
            try:
                header = row.find_element_by_tag_name("th").text
                data = row.find_element_by_tag_name("td")
                if "Erstellt von" in header:
                    self.by = data.text
                elif "Beschreibung" in header:  # Description is not in this table anymore but you can never be sure enough.
                    self.description = data.text
            except NoSuchElementException:
                pass

        if self.description == None:
            # Get description text from div below information table
            description_div = WebDriverWait(site_row, 3).until(EC.presence_of_element_located((By.XPATH, "div[1]/div/div[2]/div[2]")))
            self.description = description_div.text

        if download_attachments:
            try:
                attachment_table_body = WebDriverWait(site_row, 1).until(EC.presence_of_element_located((By.XPATH, "div[1]/div/form/table/tbody")))
                attachment_rows = attachment_table_body.find_elements_by_tag_name("tr")
                for attachment_row in attachment_rows:
                    link_element = attachment_row.find_element_by_tag_name("a")

                    download_url = urljoin(self.real_base_url, link_element.get_attribute('href'))
                    print(f"[*] Downloading Attachment : {download_url}")
                    result = download_file_from_iserv(self.driver, download_url)
                    if result:
                        print(f"[*] '{result[0]}' was downloaded")
                        self.attachments[result[0]] = {
                            "content": result[1],
                            "description": link_element.text
                        }
            except TimeoutException: # No attachments for that exercises exist
                pass
        self.figure_out_subject()


    def save(self, exercises_dir, attachment_dir):
        data = {
            "Title": self.title,
            "Description": self.description,
            "By": self.by,
            "Tags" : self.tags,
            "ViewUrl" : self.view_url,
            "StartDate": self.start_date.strftime("%d.%m.%Y %H_%M_%S"),
            "DueDate": self.due_date.strftime("%d.%m.%Y %H_%M_%S"),
            "Attachments": [],
            "New" : self.new
        }

        if self.attachments != None:
            for attachment_name in self.attachments:
                attachment = self.attachments[attachment_name]
                attachment_content = attachment["content"]
                attachment_description = attachment["description"]
                data["Attachments"].append({
                    "Name" : attachment_name,
                    "Description" : attachment_description
                })
                if attachment_dir:
                    if os.path.isdir(attachment_dir):
                        file_path = f"{attachment_dir}\\{attachment_name}"
                        print(f"[*] Saving Attachment to {file_path}")
                        file = open(file_path, mode="wb")
                        file.write(attachment_content)
                        file.close()


        exercise_path = f"{exercises_dir}\\" + f"{self.title}-{self.start_date}-{self.due_date}{self.by}.json".replace(":", "").replace("\\", "").replace("/", "").replace("?", "").replace("*", "").replace("<", "").replace(">","").replace('"', "").replace("|", "")
        print(f"[*] Saving Exercise to : {exercise_path}")
        with open(exercise_path, 'w', encoding="utf-8") as file:
            json.dump(data, file)


    @staticmethod
    def load(path):
        new_exercise = Exercise()
        data = json.load(open(path, mode="r", encoding="utf-8"))
        new_exercise.title = data["Title"]
        new_exercise.description = data["Description"]
        new_exercise.view_url = data["ViewUrl"]
        new_exercise.by = data["By"]
        if "Tags" in data:
            new_exercise.tags = data["Tags"]
        new_exercise.start_date = datetime.strptime(data["StartDate"], "%d.%m.%Y %H_%M_%S")
        new_exercise.due_date = datetime.strptime(data["DueDate"], "%d.%m.%Y %H_%M_%S")
        new_exercise.new = data["New"]
        new_exercise.figure_out_subject_based_on_tags()
        new_exercise.figure_out_subject()

        try:
            attachments = data["Attachments"]
            for attachment in attachments:
                new_exercise.attachments[attachment["Name"]] = {
                    "content" : b"",
                    "description" : attachment["Description"]
                }
        except KeyError:
            new_exercise.attachments = {}

        return new_exercise


    def __eq__(self, other):
        assert isinstance(other, Exercise)
        return self.title == other.title and self.start_date == other.start_date and self.due_date == other.due_date

    def __repr__(self):
        return f"<autoIserv.Exercise.Exercise (title='{self.title}' start_date={self.start_date} due_date={self.due_date} by='{self.by}' subject={self.subject})>"

