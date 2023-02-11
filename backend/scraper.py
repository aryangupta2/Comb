from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
from decouple import config
from selenium.webdriver.chrome.service import Service
from fuzzywuzzy import fuzz
from pydantic import BaseModel

class Review(BaseModel):
    #logo: str
    title: str
    link: str
    rating: float

class Scraper:
    def __init__(self):
        service = Service(config("CHROMEDRIVER_PATH"))
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = config("GOOGLE_CHROME_BIN", "")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        self.browser = webdriver.Chrome(service=service, options=chrome_options)

    def wait(self):
        WebDriverWait(self.browser, 0.3)

    def build_amazon_review(self, XPATH) -> Review:
        review = self.browser.find_element(By.XPATH, XPATH)

        rating_element = review.find_element(By.XPATH, ".//div[1]/div[4]/i/span")
        rating_text = rating_element.get_attribute('textContent')
        rating_float = float(rating_text[:3])

        title_element = review.find_element(By.XPATH, ".//div[1]/div[4]/span[2]")
        title_text = title_element.get_attribute('textContent')

        read_more_element = review.find_element(By.XPATH, ".//div[2]/a")
        review_hyperlink = read_more_element.get_attribute('href')
        return Review(title=title_text, link=review_hyperlink, rating=rating_float)

    def scrape(self):
        browser = self.browser

        # Search for the product
        product_name = 'Apple iPhone 13 128GB - Blue - Unlocked'
        browser.get('https://www.amazon.com/s?k=' + product_name)
        self.wait()
        
        # Get all the products from the search and click on the one that matches the most with the product name
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
        self.wait()

        # Find the rating for the product
        print(browser.title)
        rating = browser.find_element(By.XPATH, "//*[@id=\"reviewsMedley\"]/div/div[1]/span[1]/span/div[2]/div/div[2]/div/span/span")
        self.wait()
        rating_text = rating.text

        # Go the the customer review page
        see_all_reviews = browser.find_element(By.XPATH, "//*[@id=\"cr-pagination-footer-0\"]/a")
        self.wait()
        see_all_reviews.click()
        self.wait()

        # Select the top positive review
        review: Review = self.build_amazon_review("/html/body/div[1]/div[3]/div/div[1]/div/div[1]/div[1]/div/div/div[1]/div[1]")
        print(review)
        # Select the top critical review
        #critical_review = browser.find_element(By.XPATH,"//*[@id=\"viewpoint-RRMK4PYHPFNQF\"]/div[1]")



