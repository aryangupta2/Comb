from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from scraper import Scraper
from scrape_functions import *
import threading
from fastapi.middleware.cors import CORSMiddleware
import concurrent.futures


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

threadLocal = threading.local()

def create_scraper():
    scraper = getattr(threadLocal, 'scraper', None)
    if scraper is None:
        scraper = Scraper()
        setattr(threadLocal, 'scraper', scraper)
    return scraper


class CompleteResponse(BaseModel):
    stores: List[StoreReview]
    articles: List[ArticleReview]
    videos: List[VideoReview]
    article_average: float
    customer_average: float


class Item(BaseModel):
    customer_avg: float
    customer_reviews: List[Review] = []
    #article_avg: float

class Product(BaseModel):
    product_name: str

@app.get('/test/')
def get(product_name: str):
    return scrape_amazon(Scraper(), product_name)

@app.get('/ratings/')
async def get(product_name: str):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        scrape_functions = [scrape_amazon, scrape_toms_guide, scrape_youtube, scrape_bestbuy, scrape_walmart, scrape_verge, scrape_rtings]
        thread_results = [executor.submit(function, Scraper(), product_name) for function in scrape_functions]

        reviews = []
        for thread_execution in concurrent.futures.as_completed(thread_results):
            result = thread_execution.result()
            print(result)
            reviews.append(result)

        store_reviews: List[StoreReview] = []
        article_reviews: List[ArticleReview] = []
        video_reviews: List[VideoReview] = []
        article_sum = 0
        customer_sum = 0

        for review in reviews:
            if review is None:
                continue

            if isinstance(review, StoreReview):
                store_reviews.append(review)
                customer_sum += review.rating
            elif isinstance(review, ArticleReview):
                article_reviews.append(review)
                article_sum += review.rating

            else:
                video_reviews = review
        
        article_avg = 0
        if len(article_reviews) > 0:
            article_avg = article_sum/len(article_reviews)

        customer_avg = 0
        if len(store_reviews) > 0:
            customer_avg = customer_sum/len(store_reviews)

        return CompleteResponse(stores= store_reviews, articles=article_reviews, videos=video_reviews, article_average=article_avg, customer_average=customer_avg)
 
