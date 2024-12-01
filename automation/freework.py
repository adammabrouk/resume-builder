import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class FreeWorkApplier():
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.vars = {}
        self.watched = [
            "https://www.free-work.com/fr/tech-it/jobs?contracts=contractor&min_daily_rate=550&experience=intermediate&query=Big%20Data",
        ]
    
    def teardown_method(self, method):
        self.driver.quit()

    def save_cookies(self, driver):
        # Get and store cookies after login
        cookies = driver.get_cookies()

        # Store cookies in a file
        with open('cookies.json', 'w') as file:
            json.dump(cookies, file)
        print('New Cookies saved successfully')


    def load_cookies(self, driver):
        # Check if cookies file exists
        if 'cookies.json' in os.listdir():

            # Load cookies to a vaiable from a file
            with open('cookies.json', 'r') as file:
                cookies = json.load(file)

            # Set stored cookies to maintain the session
            for cookie in cookies:
                driver.add_cookie(cookie)
        else:
            print('No cookies file found')
        
        driver.refresh() # Refresh Browser after login

    def login(self):
        self.driver.get("https://www.free-work.com/fr/tech-it")
        self.driver.find_element(By.LINK_TEXT, "Connexion").click()
        self.driver.find_element(By.ID, "email").click()
        self.driver.find_element(By.ID, "email").send_keys("mabrouk.adam@outlook.com")
        self.driver.find_element(By.ID, "password").send_keys(os.environ.get("FREEWORK_PASSWORD"))
        self.driver.find_element(By.CSS_SELECTOR, "div:nth-child(5) > .w-full").click()
        self.save_cookies(self.driver)
    
    def start(self):
        try:
            self.login()
          
            for url in self.watched:

                self.driver.get(url)
                self.load_cookies(self.driver)
                self.driver.set_window_size(1392, 1028)

                # Wait for the link text to be clickable and then click
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.LINK_TEXT, "Data Analyste - Niort (H-F)"))
                ).click()
                
                # Scroll actions
                self.driver.execute_script("window.scrollTo(0, 0)")
                self.driver.execute_script("window.scrollTo(0, 2317)")
                
                # Wait for the element by CSS selector to be present
                element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".h-full:nth-child(4)"))
                )
                actions = ActionChains(self.driver)
                actions.move_to_element(element).perform()

                # Wait for the text area to be visible and send keys
                message_box = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.ID, "job-application-message"))
                )
                message_box.send_keys("Publiée le 21/11/2024\\nPartager cette offre\\n\\n...")

        except TimeoutException as e:
            print("An element was not loaded in time:", e)
        finally:
            self.teardown_method(None)

if __name__ == "__main__":
    applier = FreeWorkApplier()
    applier.start()
