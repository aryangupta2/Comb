from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import DesiredCapabilities
from decouple import config
from selenium.webdriver.chrome.service import Service



 

class Scraper:
    def __init__(self):
        service = Service(config("CHROMEDRIVER_PATH"))
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = config("GOOGLE_CHROME_BIN", "")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        #chrome_options.add_argument("start-maximized")

        caps = DesiredCapabilities().CHROME
        caps["pageLoadStrategy"] = "none"
        self.browser = webdriver.Chrome(service=service, options=chrome_options)

    def __del__(self):
        self.browser.quit() # clean up driver when we are cleaned up

    def wait(self, XPATH):
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, XPATH))
        )



