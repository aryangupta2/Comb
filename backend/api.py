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
    stores: List[StoreReview] = None
    articles: List[ArticleReview] = None
    videos: List[VideoReview] = None


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

        results = []
        for thread_execution in concurrent.futures.as_completed(thread_results):
            results.append(thread_execution.result())

        # scraper = create_scraper()
        # amazon_review: StoreReview = scrape_amazon(scraper, product_name)
        # toms_guide_review: ArticleReview = scrape_toms_guide(scraper, product_name)
        # video_reviews: List[VideoReview] = scrape_youtube(scraper, product_name)
        #return CompleteResponse(videos=video_reviews, stores=[amazon_review], articles=[toms_guide_review])
        print(results)
        return results
 
