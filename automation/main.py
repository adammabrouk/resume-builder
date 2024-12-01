from time import sleep
from selenium import webdriver # type: ignore

driver = webdriver.Chrome()
driver2 = webdriver.Chrome()

driver.get("http://selenium.dev")
driver2.get("http://google.com")

sleep(5)

driver.quit()
driver2.quit()