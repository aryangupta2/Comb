from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from scraper import Scraper
from scrape_functions import scrape_amazon, scrape_toms_guide, Review, SiteReview
import threading


app = FastAPI()

threadLocal = threading.local()

def create_scraper():
    scraper = getattr(threadLocal, 'scraper', None)
    if scraper is None:
        scraper = Scraper()
        setattr(threadLocal, 'scraper', scraper)
    return scraper

class Item(BaseModel):
    customer_avg: float
    customer_reviews: List[Review] = []
    #article_avg: float

class Product(BaseModel):
    product_name: str

@app.get('/')
def get(product: Product):
    scraper = create_scraper()
    return scrape_amazon(scraper, product.product_name)
    #return scrape__guide(scraper, product.product_name)