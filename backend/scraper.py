from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
from decouple import config
from selenium.webdriver.chrome.service import Service
from fuzzywuzzy import fuzz

class Scraper:
    def __init__(self):
        service = Service(config("CHROMEDRIVER_PATH"))
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = config("GOOGLE_CHROME_BIN", "")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        self.browser = webdriver.Chrome(service=service, options=chrome_options)

    def scrape(self):
        browser = self.browser
        product_name = 'Apple iPhone 13 128GB - Blue - Unlocked'
        browser.get('https://www.amazon.com/s?k=' + product_name)
        WebDriverWait(browser, 0.1)
        
        parent = browser.find_element(By.XPATH, "//*[@id=\"search\"]/div[1]/div[1]/div/span[1]/div[1]")
        elements = parent.find_elements(By.CLASS_NAME, "a-size-medium")
        closest_element = elements[0]
        highest_ratio = fuzz.ratio(product_name, closest_element.text)
        for element in elements:
            ratio = fuzz.ratio(product_name, element.text)
            if ratio > highest_ratio:
                closest_element = element
                highest_ratio = ratio
        print(closest_element.text)
        closest_element.click()

        WebDriverWait(browser, 0.1)
        print(browser.title)
        rating = browser.find_element(By.XPATH, "//*[@id=\"reviewsMedley\"]/div/div[1]/span[1]/span/div[2]/div/div[2]/div/span/span")
        
        WebDriverWait(browser, 0.1)
        print(rating.text)

