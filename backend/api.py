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


class Item(BaseModel):
    customer_avg: float
    customer_reviews: List[Review] = []
    #article_avg: float

class Product(BaseModel):
    product_name: str

@app.get('/ratings/')
def get(product_name: str):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        scrape_functions = [scrape_amazon, scrape_toms_guide, scrape_youtube, scrape_trusted_reviews]
        thread_results = [executor.submit(function, Scraper(), product_name) for function in scrape_functions]

        reviews = []
        for thread_execution in concurrent.futures.as_completed(thread_results):
            reviews.append(thread_execution.result())

        store_reviews: List[StoreReview] = []
        article_reviews: List[ArticleReview] = []
        video_reviews: List[VideoReview] = []

        for review in reviews:
            if isinstance(review, StoreReview):
                store_reviews.append(review)
            elif isinstance(review, ArticleReview):
                article_reviews.append(review)
            else:
                video_reviews = review
                
        return CompleteResponse(stores= store_reviews, articles=article_reviews, videos=video_reviews)
 
