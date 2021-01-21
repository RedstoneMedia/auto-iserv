from autoIserv import Session, Exercise
from autoIserv.Module import Module

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class ExerciseModule(Module):
    def __init__(self, session: Session):
        super().__init__("Aufgaben", session)


    def get_exercises(self):
        self.navigate()
        print("[*] Getting exercise Table")
        exercise_table = WebDriverWait(self.content, 5).until(EC.presence_of_element_located((By.ID, "crud-table")))
        exercise_table_body = exercise_table.find_element_by_tag_name("tbody")
        exercise_rows = WebDriverWait(exercise_table_body, 5).until(EC.presence_of_all_elements_located((By.TAG_NAME, "tr")))
        exercises = []
        for i, exercise_element in enumerate(exercise_rows):
            exercise = Exercise()
            if exercise.get_basic_data(exercise_element, i, self.session.driver, self.session.base_url):
                exercises.append(exercise)
        return exercises