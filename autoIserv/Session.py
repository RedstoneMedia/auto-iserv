from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Session:

    def __init__(self, username : str, password : str, headless : bool = True, iserv_url : str = "", use_chrome : bool = False):
        print("[*] Starting Webdriver")
        if not use_chrome:
            options = webdriver.FirefoxOptions()
            options.headless = headless
            profile = webdriver.FirefoxProfile()
            self.driver = webdriver.Firefox(firefox_options=options, firefox_profile=profile)
        else:
            print("Warning : Chrome is not relay supported and is not tested.")
            self.driver = webdriver.Chrome()
        self.base_url = iserv_url
        try:
            self.login(username, password)
        except WebDriverException as e:
            self.close()
            raise e


    def login(self, username : str, password : str):
        print("[*] Navigating to Login Page")
        self.driver.get(f"{self.base_url}/login")
        username_input = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH,"//input[@placeholder='Account']")))
        password_input = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH,"//input[@placeholder='Passwort']")))
        username_input.send_keys(username)
        password_input.send_keys(password)
        print("[*] Submitting credentials")
        login_button = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH,"//button[@type='submit']")))
        login_button.click()

        try:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[@class='sidebar sidebar-profile']")))
        except TimeoutException:
            raise ValueError("Wrong credentials")

        print("[*] Right credentials")


    def open_module(self, module_name : str):
        modules = self.driver.find_elements_by_class_name("nav-module")
        for module in modules:
            label = module.find_elements_by_class_name("item-label")[0]
            current_module_name = label.get_attribute('innerHTML')
            if current_module_name == module_name:
                link = module.find_element_by_tag_name("a").get_attribute("href")
                print(f"[*] Navigating to : {module_name}")
                self.driver.get(link)
                return link
        raise ModuleNotFoundError(f"Did not find Iserv module : {module_name}")


    def log_out(self):
        print("[*] Logging out")
        self.driver.get(f"{self.base_url}/app/logout")


    def close(self):
        print("[*] Closing browser")
        self.driver.quit()