from fuzzywuzzy import fuzz
from pydantic import BaseModel
from typing import List
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import cohere
from cohere.classify import Example
from datasets import *
import time

class VideoReview(BaseModel):
    link: str
    thumbnail_url: str

class Review(BaseModel):
    #logo: str
    title: str
    link: str
    rating: float
    sentiment: str

class StoreReview(BaseModel):
    site: str
    reviews: List[Review]
    rating: float

class ArticleReview(BaseModel):
    site: str
    link: str
    rating: float
 
def find_reviews_sentiment(review):
    co = cohere.Client('B9k2WYc1FhKhqhJQq4fNFUoVTeZ9pjZtVb6aDgOZ')
    reviews = [review]
    response = co.classify(
        model='large',
        inputs=reviews,
        examples=sentiment_examples,
    )
    return response.classifications[0].prediction

def build_top_amazon_review(scraper, XPATH) -> Review:
    review = scraper.browser.find_element(By.XPATH, XPATH)
    
    rating_element = review.find_element(By.XPATH, ".//div[1]/div[4]/i/span")
    rating_text = rating_element.get_attribute('textContent')
    rating_float = float(rating_text[:3])

    title_element = review.find_element(By.XPATH, ".//div[1]/div[4]/span[2]")
    title_text = title_element.get_attribute('textContent')

    read_more_element = review.find_element(By.XPATH, ".//div[2]/a")
    review_hyperlink = read_more_element.get_attribute('href')

    sentiment = find_reviews_sentiment(rating_text) # uses Cohere NLP
    return Review(title=title_text, link=review_hyperlink, rating=rating_float, sentiment=sentiment)

def build_amazon_review(scraper, XPATH) -> Review:
    review = scraper.browser.find_element(By.XPATH, XPATH)
    rating_element = review.find_element(By.XPATH, ".//a[1]/i/span")
    rating_text = rating_element.get_attribute('textContent')
    rating_float = float(rating_text[:3])

    title_element = review.find_element(By.XPATH, ".//a[2]/span")
    title_text = title_element.get_attribute('textContent')

    
    read_more_element = review.find_element(By.XPATH, ".//a[1]")
    review_hyperlink = read_more_element.get_attribute('href')

    sentiment = find_reviews_sentiment(rating_text) # uses Cohere NLP
    return Review(title=title_text, link=review_hyperlink, rating=rating_float, sentiment=sentiment)

def scrape_amazon(scraper, product_name) -> StoreReview:
    store = "amazon"
    browser = scraper.browser

    # Search for the product
    browser.get('https://www.amazon.com/s?k=' + product_name)
    scrollDownAllTheWay(browser)
    parent_xpath = "//*[@id=\"search\"]/div[1]/div[1]/div/span[1]/div[1]"
    scraper.wait(By.XPATH, parent_xpath)
    
    # Get all the products from the search and click on the one that matches the most with the product name
    parent = browser.find_element(By.XPATH, parent_xpath)
    elements = parent.find_elements(By.CLASS_NAME, "a-size-medium")
    closest_element = elements[0]
    highest_ratio = fuzz.ratio(product_name, closest_element.text)
    for element in elements:    
        ratio = fuzz.ratio(product_name, element.text)
        if ratio > highest_ratio:
            closest_element = element
            highest_ratio = ratio
    closest_element.click()
    
    rating_xpath = "//*[@id=\"reviewsMedley\"]/div/div[1]/span[1]/span/div[2]/div/div[2]/div/span/span"
    scraper.wait(By.XPATH, rating_xpath)

    # Find the rating for the product
    rating = browser.find_element(By.XPATH, rating_xpath)
    rating_text = rating.text
    rating_float = float(rating_text[:3])

    # Go the the customer review page
    all_reviews_xpath = "//*[@id=\"cr-pagination-footer-0\"]/a"
    all_reviews_css_selector = "a[data-hook='see-all-reviews-link-foot']"
    
    scraper.wait(By.CSS_SELECTOR, all_reviews_css_selector)

    see_all_reviews = browser.find_element(By.CSS_SELECTOR, all_reviews_css_selector)
    see_all_reviews.click()

    # Select the best positive and critical reviews
    pos_review_xpath = "/html/body/div[1]/div[3]/div/div[1]/div/div[1]/div[1]/div/div/div[1]/div[1]"
    general_review_xpath = "/html/body/div[1]/div[3]/div/div[1]/div/div[1]/div[5]/div[3]/div/div[1]/div/div/div[2]"
    WebDriverWait(browser, 10).until(lambda driver: driver.find_elements(By.XPATH, pos_review_xpath) or
                                               driver.find_elements(By.XPATH, general_review_xpath))[0]

    if len(browser.find_elements(By.XPATH, pos_review_xpath)) > 0:
        positive_review: Review = build_top_amazon_review(scraper, pos_review_xpath)
        critical_review: Review = build_top_amazon_review(scraper, "/html/body/div[1]/div[3]/div/div[1]/div/div[1]/div[1]/div/div/div[2]/div[1]")
        return StoreReview(reviews=[positive_review, critical_review], rating=rating_float, site=store)
    else:
        review_1: Review = build_amazon_review(scraper, general_review_xpath)
        review_2: Review = build_amazon_review(scraper, "/html/body/div[1]/div[3]/div/div[1]/div/div[1]/div[5]/div[3]/div/div[2]/div/div/div[2]")
        return StoreReview(reviews=[review_1, review_2], rating=rating_float, site=store)

def slice_colon(str):
    index = str.find(':')
    return str[:index]

def contains_review_str(str):
    return "review" in str.lowercase()

# UNFINISHED, DOES NOT WORK
def scrape_trusted_reviews(scraper, product_name) -> ArticleReview:
    browser = scraper.browser

    # Search for the product
    browser.get('https://www.trustedreviews.com/?s=' + product_name)
    list_xpath = '//*[@id="content"]/article/section[2]/div[1]/ul'
    scraper.wait(By.XPATH, list_xpath)

    # Get all of the products from the search and click on the one that matches most with product name
    parent = browser.find_element(By.XPATH, list_xpath)
    elements = parent.find_elements(By.TAG_NAME, 'li')
    print(elements[0].text)
    closest_element = elements[0]
    highest_ratio = fuzz.ratio(product_name, slice_colon(closest_element.text))
    for element in elements:
        element_text = element.text
        print(element_text)
        if not contains_review_str(element_text):
            continue
        ratio = fuzz.ratio(product_name, slice_colon(element_text))
        if ratio > highest_ratio:
            closest_element = elements
            highest_ratio = ratio
    if highest_ratio < 20:
        return None
    closest_element.click()

    # Rating is not displayed in text, but with pictures instead
    # Hacky method to add the number of stars and convert that to an out of 5 rating
    star_parent_class = "score-stars score-stars--large"
    scraper.wait(By.CLASS_NAME, star_parent_class)

    star_parent = browser.find_element(By.CLASS_NAME, star_parent_class)
    stars = star_parent.find_elements(By.CSS_SELECTOR, "img[data-src='wp-content/themes/kiara-child-theme/assets/image/tr__fullstar.svg']")
    half_stars = star_parent.find_elements(By.CSS_SELECTOR, "img[data-src='wp-content/themes/kiara-child-theme/assets/image/tr__halfstar.svg']")
    rating: float = len(stars)
    if(len(half_stars)) > 0:
        rating -= 0.5

    article_hyperlink = browser.current_url

    return ArticleReview(rating=rating, link=article_hyperlink, site="trusted-reviews")

def scrape_walmart(scraper, product_name) -> StoreReview:
    browser = scraper.browser
    store = "walmart"

    browser.get("https://www.walmart.ca/search?q=" + product_name)
    # Search for the product
    parent_ID = "product-results"
    #print(browser.page_source)
    WebDriverWait(browser, 1)
    print(browser.find_elements(By.XPATH, ".//*"))
    scraper.wait(By.ID, parent_ID)
    
    
    # Get all the products from the search and click on the one that matches the most with the product name
    parent = browser.find_element(By.ID, parent_ID)
    elements = parent.find_elements(By.XPATH, ".//*")
    #"/html/body/div[1]/div[1]/div[3]/div/div[2]/div/div/div[8]/div[2]/div[2]/div[1]/div/div[1]"
    #"/html/body/div[1]/div[1]/div[3]/div/div[2]/div/div/div[8]/div[2]/div[2]/div[1]/div/div[1]/div[1]/div/a/div/div[2]/div[2]/span/div/p"
    closest_element = elements[0]
    highest_ratio = fuzz.ratio(product_name, closest_element.text)
    for element in elements:
        text_element = element.find_element(By.TAG_NAME, "p")
        element_text = text_element.text
        print(element_text)
        ratio = fuzz.ratio(product_name, element_text)
        if ratio > highest_ratio:
            closest_element = element
            highest_ratio = ratio
    closest_element.click()
    
    rating_xpath = "//*[@id=\"reviewsMedley\"]/div/div[1]/span[1]/span/div[2]/div/div[2]/div/span/span"
    scraper.wait(By.XPATH, rating_xpath)

    # Find the rating for the product
    rating = browser.find_element(By.XPATH, rating_xpath)
    rating_text = rating.text
    rating_float = float(rating_text[:3])

    # Go the the customer review page
    all_reviews_xpath = "//*[@id=\"cr-pagination-footer-0\"]/a"
    all_reviews_css_selector = "a[data-hook='see-all-reviews-link-foot']"
    
    scraper.wait(By.CSS_SELECTOR, all_reviews_css_selector)

    see_all_reviews = browser.find_element(By.CSS_SELECTOR, all_reviews_css_selector)
    see_all_reviews.click()

    # Select the best positive and critical reviews
    pos_review_xpath = "/html/body/div[1]/div[3]/div/div[1]/div/div[1]/div[1]/div/div/div[1]/div[1]"
    general_review_xpath = "/html/body/div[1]/div[3]/div/div[1]/div/div[1]/div[5]/div[3]/div/div[1]/div/div/div[2]"
    WebDriverWait(browser, 10).until(lambda driver: driver.find_elements(By.XPATH, pos_review_xpath) or
                                               driver.find_elements(By.XPATH, general_review_xpath))[0]

    if len(browser.find_elements(By.XPATH, pos_review_xpath)) > 0:
        positive_review: Review = build_top_amazon_review(scraper, pos_review_xpath)
        critical_review: Review = build_top_amazon_review(scraper, "/html/body/div[1]/div[3]/div/div[1]/div/div[1]/div[1]/div/div/div[2]/div[1]")
        return StoreReview(reviews=[positive_review, critical_review], rating=rating_float, site=store)
    else:
        review_1: Review = build_amazon_review(scraper, general_review_xpath)
        review_2: Review = build_amazon_review(scraper, "/html/body/div[1]/div[3]/div/div[1]/div/div[1]/div[5]/div[3]/div/div[2]/div/div/div[2]")
        return StoreReview(reviews=[review_1, review_2], rating=rating_float, site=store)
# Above is UNFINISHED

def scrollDown(driver, value):
    driver.execute_script("window.scrollBy(0,"+str(value)+")")

# Scroll down the page
def scrollDownAllTheWay(driver):
    old_page = driver.page_source
    while True:
        for i in range(2):
            scrollDown(driver, 500)
            time.sleep(2)

        new_page = driver.page_source
        if new_page != old_page:
            old_page = new_page
        else:
            break
    return True

def scrape_bestbuy(scraper, product_name) -> StoreReview:
    browser = scraper.browser
    store = "bestbuy"

    

    browser.get("https://www.bestbuy.ca/en-ca/search?search=" + product_name)

    # soup = BeautifulSoup(browser.page_source, 'lxml')
    # items = []
    # items_selector = soup.select('a[itemprop="url"]')
    # print(items_selector)

    scrollDownAllTheWay(browser)
    
    # Get all the products from the search and click on the one that matches the most with the product name
    parent = browser.find_element(By.XPATH, parent_XPATH)
    elements = parent.find_elements(By.XPATH, ".//*")
    #"/html/body/div[1]/div[1]/div[3]/div/div[2]/div/div/div[8]/div[2]/div[2]/div[1]/div/div[1]"
    #"/html/body/div[1]/div[1]/div[3]/div/div[2]/div/div/div[8]/div[2]/div[2]/div[1]/div/div[1]/div[1]/div/a/div/div[2]/div[2]/span/div/p"
    closest_element = elements[0]
    highest_ratio = fuzz.ratio(product_name, closest_element.text)
    for element in elements:
        text_element = element.find_element(By.TAG_NAME, "p")
        element_text = text_element.text
        print(element_text)
        ratio = fuzz.ratio(product_name, element_text)
        if ratio > highest_ratio:
            closest_element = element
            highest_ratio = ratio
    closest_element.click()
    
    rating_xpath = "//*[@id=\"reviewsMedley\"]/div/div[1]/span[1]/span/div[2]/div/div[2]/div/span/span"
    scraper.wait(By.XPATH, rating_xpath)

    # Find the rating for the product
    rating = browser.find_element(By.XPATH, rating_xpath)
    rating_text = rating.text
    rating_float = float(rating_text[:3])

    # Go the the customer review page
    all_reviews_xpath = "//*[@id=\"cr-pagination-footer-0\"]/a"
    all_reviews_css_selector = "a[data-hook='see-all-reviews-link-foot']"
    
    scraper.wait(By.CSS_SELECTOR, all_reviews_css_selector)

    see_all_reviews = browser.find_element(By.CSS_SELECTOR, all_reviews_css_selector)
    see_all_reviews.click()

    # Select the best positive and critical reviews
    pos_review_xpath = "/html/body/div[1]/div[3]/div/div[1]/div/div[1]/div[1]/div/div/div[1]/div[1]"
    general_review_xpath = "/html/body/div[1]/div[3]/div/div[1]/div/div[1]/div[5]/div[3]/div/div[1]/div/div/div[2]"
    WebDriverWait(browser, 10).until(lambda driver: driver.find_elements(By.XPATH, pos_review_xpath) or
                                               driver.find_elements(By.XPATH, general_review_xpath))[0]

    if len(browser.find_elements(By.XPATH, pos_review_xpath)) > 0:
        positive_review: Review = build_top_amazon_review(scraper, pos_review_xpath)
        critical_review: Review = build_top_amazon_review(scraper, "/html/body/div[1]/div[3]/div/div[1]/div/div[1]/div[1]/div/div/div[2]/div[1]")
        return StoreReview(reviews=[positive_review, critical_review], rating=rating_float, site=store)
    else:
        review_1: Review = build_amazon_review(scraper, general_review_xpath)
        review_2: Review = build_amazon_review(scraper, "/html/body/div[1]/div[3]/div/div[1]/div/div[1]/div[5]/div[3]/div/div[2]/div/div/div[2]")
        return StoreReview(reviews=[review_1, review_2], rating=rating_float, site=store)
# Above is UNFINISHED

def scrape_toms_guide(scraper, product_name) -> ArticleReview:
    browser = scraper.browser

    # Search for the product
    browser.get('https://www.tomsguide.com/search?searchTerm=' + product_name)
    list_xpath = "//*[@id=\"content\"]/section/div[2]"
    scraper.wait(By.XPATH, list_xpath)

    # Get all the products from the search and click on the one that matches the most with the product name
    parent = browser.find_element(By.XPATH, list_xpath)
    elements = parent.find_elements(By.CLASS_NAME, "article-name")
    closest_element = elements[0]
    highest_ratio = fuzz.ratio(product_name, slice_colon(closest_element.text))
    for element in elements:    
        ratio = fuzz.ratio(product_name, slice_colon(element.text))
        if ratio > highest_ratio:
            closest_element = element
            highest_ratio = ratio
    closest_element.click()

    star_parent_class = "chunk"
    scraper.wait(By.CLASS_NAME, star_parent_class)

    star_parent = browser.find_element(By.CLASS_NAME, star_parent_class)
    stars = star_parent.find_elements(By.CSS_SELECTOR, "*")
    half_stars = star_parent.find_elements(By.CLASS_NAME, "half")
    rating: float = len(stars)
    if(len(half_stars)) > 0:
        rating -= 0.5

    article_hyperlink = browser.current_url
    
    return ArticleReview(rating=rating, link=article_hyperlink, site='toms-guide')

def scrape_youtube(scraper, product_name):
    browser = scraper.browser
    product_name += ' Review'
    browser.get("https://www.youtube.com/results?search_query=" + product_name)

    parent_xpath = "//*[@id=\"contents\"]"
    scraper.wait(By.XPATH, parent_xpath)
    
    # Get all the products from the search and click on the one that matches the most with the product name
    parent = browser.find_element(By.XPATH, parent_xpath)
    elements = parent.find_elements(By.TAG_NAME, "ytd-video-renderer")
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    tuples = []

    for element in elements:
        browser.execute_script("arguments[0].scrollIntoView();", element)
        scraper.wait(By.ID, "video-title")
        title_wrap_element = element.find_element(By.ID, "video-title")
        title_element = title_wrap_element.find_element(By.TAG_NAME, "yt-formatted-string")
        title_text = title_element.text
        if "review" not in title_text.lower():
            continue
        print(title_element)
        ratio = fuzz.ratio(product_name, title_text)
        tuples.append((ratio, element))

    sorted_tuples = sorted(tuples, key=lambda tup: tup[0], reverse=True)
        
    sorted_tuples = sorted_tuples[:5]

    video_reviews: List[VideoReview] = []

    print(tuples)
    print(sorted_tuples)
    
    for best_video_tuple in tuples:
        video_element = best_video_tuple[1]

        yt_img_element = video_element.find_element(By.TAG_NAME, 'yt-image')
        img_element = yt_img_element.find_element(By.TAG_NAME, 'img')
        img_src = img_element.get_attribute('src')

        thumbnail_element = video_element.find_element(By.ID, 'thumbnail')
        video_link = thumbnail_element.get_attribute('href')

        print(video_link)
        print(img_src)

        if None == video_link or None == img_src:
            continue

        video_reviews.append(VideoReview(link=video_link, thumbnail_url=img_src))
    
    return video_reviews


