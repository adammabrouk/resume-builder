# Generated by Selenium IDE
import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class TestLogin():
  def setup_method(self, method):
    self.driver = webdriver.Chrome()
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def test_login(self):
    self.driver.get("https://www.free-work.com/fr/tech-it")
    self.driver.set_window_size(1392, 1028)
    self.driver.find_element(By.LINK_TEXT, "Connexion").click()
    self.driver.find_element(By.ID, "email").click()
    self.driver.find_element(By.ID, "email").send_keys("mabrouk.adam@outlook.com")
    self.driver.find_element(By.ID, "password").send_keys("Sanandreas200@")
    self.driver.find_element(By.CSS_SELECTOR, "div:nth-child(5) > .w-full").click()
    element = self.driver.find_element(By.CSS_SELECTOR, "div:nth-child(5) > .w-full")
    actions = ActionChains(self.driver)
    actions.move_to_element(element).perform()
    element = self.driver.find_element(By.CSS_SELECTOR, "body")
    actions = ActionChains(self.driver)
    actions.move_to_element(element, 0, 0).perform()
    self.driver.find_element(By.CSS_SELECTOR, ".md\\3A col-span-1:nth-child(2) .block > .absolute").click()
  
