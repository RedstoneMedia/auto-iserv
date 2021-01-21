from autoIserv import Session, Email
from autoIserv.Module import Module

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class EmailModule(Module):

    def __init__(self, session : Session):
        super().__init__("E-Mail", session)

    def get_emails(self):
        self.navigate()
        print("[*] Getting email rows")
        email_rows = WebDriverWait(self.content, 3).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "message-row")))
        emails = []
        for i, email in enumerate(email_rows):
            email_obj = Email()
            email_obj.get_basic_data(email, i, self.session.driver, self.session.base_url)
            emails.append(email_obj)
        return emails