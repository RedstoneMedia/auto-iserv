from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from autoIserv import Session

import time

class Module:

    def __init__(self, module_name, session: Session):
        self.module_name = module_name
        self.session = session
        # Contains content of the current module not the sidebar
        self.content = None # type: WebElement


    def navigate(self):
        self.session.open_module(self.module_name)
        time.sleep(1)  # Don't know why but it works with this
        self.set_content()


    def set_content(self):
        self.content = WebDriverWait(self.session.driver, 3).until(EC.presence_of_element_located((By.ID, "content")))
