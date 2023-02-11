from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from scraper import Scraper
from scrape_functions import scrape_amazon, scrape_toms_guide, scrape_youtube, Review, StoreReview, ArticleReview, VideoReview
import threading
from fastapi.middleware.cors import CORSMiddleware


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
    print(product_name)
    scraper = create_scraper()
    amazon_review: StoreReview = scrape_amazon(scraper, product_name)
    toms_guide_review: ArticleReview = scrape_toms_guide(scraper, product_name)
    video_reviews: List[VideoReview] = scrape_youtube(scraper, product_name)
    return CompleteResponse(videos=video_reviews, stores=[amazon_review], articles=[toms_guide_review])
