from fuzzywuzzy import fuzz
from pydantic import BaseModel
from typing import List
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
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
# positive
# neutral
# negative
def find_reviews_sentiment(review):
    co = cohere.Client('B9k2WYc1FhKhqhJQq4fNFUoVTeZ9pjZtVb6aDgOZ')
    reviews = [review]
    response = co.classify(
        model='large',
        inputs=reviews,
        examples=sentiment_examples,
    )
    return response.classifications[0].prediction

def find_titles_informativeness(title):
    co = cohere.Client('B9k2WYc1FhKhqhJQq4fNFUoVTeZ9pjZtVb6aDgOZ')
    titles = [title]
    response = co.classify(
        model='large',
        inputs=titles,
        examples=clickbait_examples,
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
    scrollDownAllTheWay(browser, 200)
    parent_xpath = "/html/body/div[1]/div[2]/div[1]/div[1]/div/span[1]/div[1]"
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
    try:
        scraper.wait(By.XPATH, rating_xpath)
    except:
        return None

    # Find the rating for the product
    rating = browser.find_element(By.XPATH, rating_xpath)
    rating_text = rating.text
    rating_float = float(rating_text[:3])

    # Go the the customer review page
    all_reviews_css_selector = "a[data-hook='see-all-reviews-link-foot']"
    
    scraper.wait(By.CSS_SELECTOR, all_reviews_css_selector)

    see_all_reviews = browser.find_element(By.CSS_SELECTOR, all_reviews_css_selector)
    see_all_reviews.click()
    paths = [   "/html/body/div[1]/div[3]/div/div[1]/div/div[1]/div[1]/div/div/div[1]/div[1]",
                "/html/body/div[1]/div[3]/div/div[1]/div/div[1]/div[1]/div/div/div[2]/div[1]",
                "/html/body/div[1]/div[3]/div/div[1]/div/div[1]/div[5]/div[3]/div/div[3]/div/div/div[2]"
                "/html/body/div[1]/div[3]/div/div[1]/div/div[1]/div[5]/div[3]/div/div[4]/div/div/div[2]"
                ]
    
    # Select the best positive and critical reviews
    reviews = []

    scrollDownAllTheWay(browser, 2)

    print(browser.current_url)
    for path in paths:
        try:
            review: Review = build_top_amazon_review(scraper, path)
            reviews.append(review)
        except:
            try:
                review: Review = build_amazon_review(scraper, path)
                reviews.append(review)
            except:
                pass
        
    
    return StoreReview(reviews=reviews, rating=rating_float, site=store)

def slice_colon(str):
    index = str.find(':')
    return str[:index]

def contains_review_str(str):
    return "review" in str.lower()

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
    closest_element = elements[0]
    highest_ratio = fuzz.ratio(product_name, slice_colon(closest_element.text))
    for element in elements:
        element_text = element.text
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
    scrollDownAllTheWay(browser, 3)

    # Get all the products from the search and click on the one that matches the most with the product name
 
    elements = browser.find_elements(By.TAG_NAME, "p")
    #"/html/body/div[1]/div[1]/div[3]/div/div[2]/div/div/div[8]/div[2]/div[2]/div[1]/div/div[1]"
    #"/html/body/div[1]/div[1]/div[3]/div/div[2]/div/div/div[8]/div[2]/div[2]/div[1]/div/div[1]/div[1]/div/a/div/div[2]/div[2]/span/div/p"
    closest_element = elements[0]
    highest_ratio = fuzz.ratio(product_name, closest_element.text)
    for element in elements:
        if element.get_attribute('data-automation') != "name":
            continue
        element_text = element.text
        ratio = fuzz.ratio(product_name, element_text)
        if ratio > highest_ratio:
            closest_element = element
            highest_ratio = ratio
    closest_element.click()

    scrollDownAllTheWay(browser, 3)
    #elements = browser.find_element(By.TAG_NAME, 'section')
    rating_float = 0.0
    try:
        rating_element = browser.find_element(By.XPATH,"/html/body/div[1]/div/div[4]/div/div/div[2]/div[1]/div[1]/div[1]/div/div[8]/div/div[2]//div/div/div[2]/div[2]/div[2]/section/div/div/div[1]")
        rating_text = rating_element.text
        rating_float = float(rating_text)
    except:
        return None

    first_review_xpath = "/html/body/div[1]/div/div[4]/div/div/div[2]/div[1]/div[1]/div[1]/div/div[8]/div/div[2]//div/div/div[6]/div[1]/div/div/div/div/div[1]"
    second_review_xpath = "/html/body/div[1]/div/div[4]/div/div/div[2]/div[1]/div[1]/div[1]/div/div[8]/div/div[2]//div/div/div[6]/div[2]/div/div/div/div/div[1]"

    reviews: List[Review] = []
    try:
        scraper.wait(By.XPATH, first_review_xpath)
        review = build_walmart_review(scraper, first_review_xpath)
        reviews.append(review)
    except:
        pass

    try:
        scraper.wait(By.XPATH, second_review_xpath)
        review = build_walmart_review(scraper, second_review_xpath)
        reviews.append(review)
    except:
        pass

    return StoreReview(reviews=reviews, rating = rating_float, site=store)

def build_walmart_review(scraper, xpath):
    element = scraper.browser.find_element(By.XPATH, xpath)
    meta_rating = element.find_element(By.XPATH, './/meta[2]')
    rating = meta_rating.get_attribute('ratingValue')

    text_element = element.find_element(By.XPATH,".//div[2]/h3")
    title_text = text_element.text

    review_p = element.find_element(By.TAG_NAME, 'p')
    review_span = review_p.find_element(By.XPATH, './/span')
    review_text = review_span.text

    sentiment = find_reviews_sentiment(review_text) # uses Cohere NLP

    return Review(title=title_text, link=scraper.browser.current_url, sentiment= sentiment, rating=rating)

# Above is UNFINISHED

def scrollDown(driver, value):
    driver.execute_script("window.scrollBy(0,"+str(value)+")")

# Scroll down the page
def scrollDownAllTheWay(driver, nb):
    old_page = driver.page_source
    while nb > 0:
        for i in range(2):
            scrollDown(driver, 500)
            time.sleep(2)

        new_page = driver.page_source
        if new_page != old_page:
            old_page = new_page
        else:
            break

        nb -= 1
    return True

def scrape_bestbuy(scraper, product_name) -> StoreReview:
    browser = scraper.browser
    store = "bestbuy"

    

    browser.get("https://www.bestbuy.ca/en-ca/search?search=" + product_name)

    # soup = BeautifulSoup(browser.page_source, 'lxml')
    # items = []
    # items_selector = soup.select('a[itemprop="url"]')

    scrollDownAllTheWay(browser, 1000)
    
    # Get all the products from the search and click on the one that matches the most with the product name
    #parent = browser.find_element(By.XPATH, parent_XPATH)
    elements = browser.find_elements(By.TAG_NAME, "a")
    elements = [element for element in elements if element.get_attribute('itemprop') is not None]
    
    #"/html/body/div[1]/div[1]/div[3]/div/div[2]/div/div/div[8]/div[2]/div[2]/div[1]/div/div[1]"
    #"/html/body/div[1]/div[1]/div[3]/div/div[2]/div/div/div[8]/div[2]/div[2]/div[1]/div/div[1]/div[1]/div/a/div/div[2]/div[2]/span/div/p"
    if len(elements) == 0:
        return None

    closest_element = elements[0]
    highest_ratio = fuzz.ratio(product_name, closest_element.text)
    for element in elements:
        text_element = element.find_element(By.TAG_NAME, "div")
        element_text = text_element.text
        ratio = fuzz.ratio(product_name, element_text)
        if ratio > highest_ratio:
            closest_element = element
            highest_ratio = ratio
    closest_element.click()
    print(browser.current_url)
    
    rating_xpath = "/html/body/div[1]/div/div[4]/section[3]/div[1]/div[2]/div[1]/div[2]/label/strong"
    
    try:
        scraper.wait(By.XPATH, rating_xpath)

        # Find the rating for the product
        rating = browser.find_element(By.XPATH, rating_xpath)
        rating_float = float(rating.text)

        rating.click()
    except:
        return None

    first_review_xpath = "/html/body/div[1]/div/div[4]/div/div[2]/div/div[1]/div/div/div/div/div/div[3]/ul/li[1]/div/div"
    second_review_xpath = "/html/body/div[1]/div/div[4]/div/div[2]/div/div[1]/div/div/div/div/div/div[3]/ul/li[2]/div/div"

    reviews: List[Review] = []
    try:
        scraper.wait(By.XPATH, first_review_xpath)
        review = build_bestbuy_review(scraper, first_review_xpath)
        reviews.append(review)
    except:
        pass

    try:
        scraper.wait(By.XPATH, second_review_xpath)
        review = build_bestbuy_review(scraper, second_review_xpath)
        reviews.append(review)
    except:
        pass

    # Select the best positive and critical reviews
    
    return StoreReview(reviews=reviews, rating = rating_float, site=store)

def build_bestbuy_review(scraper, xpath): 
    element = scraper.browser.find_element(By.XPATH, xpath)
    span_element = element.find_element(By.TAG_NAME, 'span')
    title_text = span_element.text

    review_p = element.find_element(By.TAG_NAME, 'p')
    review_span = review_p.find_element(By.XPATH, './/span')
    review_text = review_span.text

    sentiment = find_reviews_sentiment(review_text) # uses Cohere NLP

    rating = 3.0
    if sentiment == "positive":
        rating = 5.0
    elif sentiment == "negative":
        rating = 1.0

    return Review(title=title_text, link=scraper.browser.current_url, sentiment= sentiment, rating=rating)
    
# Above is UNFINISHED

def scrape_toms_guide(scraper, product_name) -> ArticleReview:
    browser = scraper.browser

    # Search for the product
    browser.get('https://www.tomsguide.com/search?searchTerm=' + product_name)
    print(browser.current_url)
    list_xpath = "//*[@id=\"content\"]/section/div[2]"
    scraper.wait(By.XPATH, list_xpath)

    # Get all the products from the search and click on the one that matches the most with the product name
    parent = browser.find_element(By.XPATH, list_xpath)
    elements = parent.find_elements(By.CLASS_NAME, "article-name")
    closest_element = elements[0]
    highest_ratio = fuzz.ratio(product_name, slice_colon(closest_element.text))
    for element in elements:    
        sliced_text = slice_colon(element.text)
        if "review" not in sliced_text.lower():
            continue
        ratio = fuzz.ratio(product_name, sliced_text)
        if ratio > highest_ratio:
            closest_element = element
            highest_ratio = ratio
    if highest_ratio < 20:
        return None
    closest_element.click()
    print(browser.current_url)

    star_parent_class = "chunk"
    try:
        scraper.wait(By.CLASS_NAME, star_parent_class)
    except:
        return None

    star_parent = browser.find_element(By.CLASS_NAME, star_parent_class)
    stars = star_parent.find_elements(By.CSS_SELECTOR, "*")
    half_stars = star_parent.find_elements(By.CLASS_NAME, "half")
    rating: float = len(stars)
    if(len(half_stars)) > 0:
        rating -= 0.5

    article_hyperlink = browser.current_url
    
    return ArticleReview(rating=rating, link=article_hyperlink, site='toms-guide')
    
def scrape_rtings(scraper, product_name):
    
    product_name += ' Review'
    browser = scraper.browser

    # Search for the product
    browser.get("https://www.rtings.com/search?q=" + product_name)

    scrollDownAllTheWay(browser, 2)
    list_xpath = "/html/body/div/div[3]/div/em/em/ol"
    scraper.wait(By.XPATH, list_xpath)

    # Get all the products from the search and click on the one that matches the most with the product name
    parent = browser.find_element(By.XPATH, list_xpath)
    elements = parent.find_elements(By.TAG_NAME, "a")
    closest_element = elements[0]
    highest_ratio = fuzz.ratio(product_name, slice_colon(closest_element.text))
    for element in elements:
        text = element.text
        ratio = fuzz.ratio(product_name, slice_colon(text))
        if ratio > highest_ratio:
            closest_element = element
            highest_ratio = ratio
    if highest_ratio < 20:
        return None
    browser.execute_script("arguments[0].click();", closest_element) 

    rating_element = browser.find_element(By.XPATH, "/html/body/div/div[3]/div[1]/div[2]/div[2]/div[2]/div/div[1]/div[1]/div/span/span")
    rating_text = rating_element.text
    rating = float(rating_text)/2
    

    article_hyperlink = browser.current_url
    
    return ArticleReview(rating=rating, link=article_hyperlink, site='rtings')

def scrape_verge(scraper, product_name):
    
    product_name += ' Review'
    browser = scraper.browser

    # Search for the product
    browser.get("https://www.theverge.com/search?q=" + product_name)

    scrollDownAllTheWay(browser, 2)
    list_xpath = "/html/body/div/main/div[2]/div/div[1]"
    scraper.wait(By.XPATH, list_xpath)

    # Get all the products from the search and click on the one that matches the most with the product name
    parent = browser.find_element(By.XPATH, list_xpath)
    elements = parent.find_elements(By.TAG_NAME, "a")
    closest_element = elements[0]
    highest_ratio = fuzz.ratio(product_name, slice_colon(closest_element.text))
    for element in elements:
        text = slice_colon(element.text)
        if not contains_review_str(text):
            continue
        ratio = fuzz.ratio(product_name, text)
        if ratio > highest_ratio:
            closest_element = element
            highest_ratio = ratio
    if highest_ratio < 20 or not contains_review_str(closest_element.text):
        return None
    closest_element.click()

    spans = browser.find_elements(By.TAG_NAME, 'span')
    prev = None
    for span in spans:
        if span.text.lower() == "verge score":
            break
        prev = span
    if prev is None:
        rating = 3.0
    else:
        span_element = prev
        rating_text = span_element.text
        rating = float(rating_text)/2

    article_hyperlink = browser.current_url
    
    return ArticleReview(rating=rating, link=article_hyperlink, site='verge')

def scrape_youtube(scraper, product_name):
    browser = scraper.browser
    product_name += ' Review'
    browser.get("https://www.youtube.com/results?search_query=" + product_name)

    scrollDownAllTheWay(browser, 2)

    parent_xpath = "//*[@id=\"contents\"]"
    scraper.wait(By.XPATH, parent_xpath)
    
    # Get all the products from the search and click on the one that matches the most with the product name
    parent = browser.find_element(By.XPATH, parent_xpath)
    elements = parent.find_elements(By.TAG_NAME, "ytd-video-renderer")
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    tuples = []

    for element in elements:
        browser.execute_script("arguments[0].scrollIntoView();", element)
        try:
            scraper.wait(By.ID, "video-title")
            title_wrap_element = element.find_element(By.ID, "video-title")
            title_element = title_wrap_element.find_element(By.TAG_NAME, "yt-formatted-string")
            title_text = title_element.text
            if "review" not in title_text.lower():
                continue
            ratio = fuzz.ratio(product_name, title_text)
            tuples.append((ratio, element))
        except:
            pass

    sorted_tuples = sorted(tuples, key=lambda tup: tup[0], reverse=True)
        
    sorted_tuples = sorted_tuples[:5]

    video_reviews: List[VideoReview] = []
    
    for best_video_tuple in sorted_tuples:
        video_element = best_video_tuple[1]

        yt_img_element = video_element.find_element(By.TAG_NAME, 'yt-image')
        img_element = yt_img_element.find_element(By.TAG_NAME, 'img')
        img_src = img_element.get_attribute('src')

        thumbnail_element = video_element.find_element(By.ID, 'thumbnail')
        video_link = thumbnail_element.get_attribute('href')

        if None == video_link or None == img_src:
            continue

        video_reviews.append(VideoReview(link=video_link, thumbnail_url=img_src))
    
    return video_reviews


