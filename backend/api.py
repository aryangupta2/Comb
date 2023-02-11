from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from scraper import Scraper


app = FastAPI()
scraper = Scraper()

class Review(BaseModel):
    #logo: str
    author: str
    body: str

class Item(BaseModel):
    customer_avg: float
    customer_reviews: List[Review] = []
    #article_avg: float

@app.get('/')
def get():
    scraper.scrape()
    return "Hello"