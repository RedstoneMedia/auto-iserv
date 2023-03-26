from .. import Session, util
from ..Module import Module

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By
import time
import datetime
import pathlib


class FilesModule(Module):

    def __init__(self, session: Session):
        super().__init__("Dateien", session)


    def get_nav_bar_folder_elements(self):
        nav_bar = WebDriverWait(self.content, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "navbar-nav")))  # type: WebElement
        nav_bar_file_links = nav_bar.find_elements_by_class_name("files-link")
        return nav_bar_file_links


    def change_to_nav_bar_folder(self, name: str):
        for folder_element in self.get_nav_bar_folder_elements():
            if folder_element.text == name:
                self.change_to_folder(folder_element.get_attribute("href"))


    def get_current_dir_files_and_dirs(self, ignore_size=False):
        file_table = self.content.find_element_by_id("files").find_element_by_tag_name("tbody")

        ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)
        rows = WebDriverWait(file_table, 3, ignored_exceptions=ignored_exceptions).until(EC.presence_of_all_elements_located((By.TAG_NAME, "tr")))

        for row in rows: # type: WebElement
            file = File.from_element(row, ignore_size)
            if file != None:
                yield file


    def change_to_folder(self, remote_location: str):
        self.session.driver.get(remote_location)
        time.sleep(1)
        self.set_content()


class File:

    FILE_LIST_COLUMN_DATA_TYPE_ORDER = ["id", "name", "size", "type", "owner", "last_change"]

    def __init__(self):
        self.id = ""
        self.name = ""
        self.size = 0
        self.type = ""
        self.owner = ""
        self.remote_location = ""
        self.last_change = None # type: datetime.datetime


    @staticmethod
    def from_element(element: WebElement, ignore_size=False):
        try:
            ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)
            WebDriverWait(element, 3, ignored_exceptions=ignored_exceptions).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "files-id")))  # type: WebElement
        except TimeoutException:
            return None
        file = File()
        for i, col in enumerate(element.find_elements_by_tag_name("td")):
            if i >= len(File.FILE_LIST_COLUMN_DATA_TYPE_ORDER):
                continue
            data_type = File.FILE_LIST_COLUMN_DATA_TYPE_ORDER[i]
            if data_type == "id":
                file.id = col.find_element_by_tag_name("input").get_attribute("value")
            elif data_type == "name":
                file.name = col.text
                file.remote_location = col.find_element_by_tag_name("a").get_attribute("href").replace("?show=true", "")
            elif data_type == "size":
                try:
                    calc_size_button = col.find_element_by_tag_name("button")
                    if not ignore_size:
                        calc_size_button.click()
                        while col.text == "berechnen":
                            time.sleep(0.1)
                        file.parse_size(col.text)
                except NoSuchElementException:
                    file.parse_size(col.text)
            elif data_type == "type":
                file.type = col.text
            elif data_type == "owner":
                file.owner = col.text
            elif data_type == "last_change":
                file.parse_last_change(col.text)
        return file


    def parse_size(self, size_text: str):
        size_text = size_text.replace(" KB", "")
        size_text = size_text.replace(".", "")
        size_text = size_text.replace(",", "")
        if size_text == "":
            time.sleep(1)
            self.size = 0
            return
        self.size = int(size_text)


    def parse_last_change(self, last_change_text):
        self.last_change = datetime.datetime.strptime(last_change_text, "%d.%m.%Y %H:%M")


    def navigate(self, session: Session):
        session.driver.get(self.remote_location)


    def download(self, session: Session, save_to: pathlib.Path):
        if self.type in ["Datei", "Archiv"]:
            _, content = util.download_file_from_iserv(session.driver, self.remote_location)
            f = open(str(save_to.joinpath(self.name)), mode="wb")
            f.write(content)
            f.close()
        else:
            raise IsADirectoryError("Folders can not be downloaded")


    def __repr__(self):
        return f"<File name={self.name} type={self.type} size={self.size} owner={self.owner} last_change={self.last_change} remote_location={self.remote_location}>"