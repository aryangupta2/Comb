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

@app.get('/preloaded/')
def get(product_name: str):
    time.sleep(5)
    return {
    "stores": [
        {
            "site": "amazon",
            "reviews": [
                {
                    "title": "Surprised me",
                    "link": "https://www.amazon.com/gp/customer-reviews/R1NQPBC3OGEX0/ref=cm_cr_arp_d_rvw_ttl?ie=UTF8&ASIN=B09JFJ1Q5C",
                    "rating": 5.0,
                    "sentiment": "positive"
                }
            ],
            "rating": 4.6
        }
    ],
    "articles": [
        {
            "site": "rtings",
            "link": "https://www.rtings.com/mouse/reviews/apple/magic-mouse-2",
            "rating": 3.0
        },
        {
            "site": "the-verge",
            "link": "https://www.theverge.com/21524288/apple-iphone-12-pro-review",
            "rating": 1.0
        },
        {
            "site": "toms-guide",
            "link": "https://www.tomsguide.com/reviews/iphone-14-pro",
            "rating": 4.5
        }
    ],
    "videos": [
        {
            "link": "https://www.youtube.com/watch?v=z_cazxB7We4",
            "thumbnail_url": "https://i.ytimg.com/vi/z_cazxB7We4/hq720.jpg?sqp=-oaymwEcCNAFEJQDSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLAh2epNf4u8utJfo-uSIp6GMuf98w"
        },
        {
            "link": "https://www.youtube.com/watch?v=K0L_9Ln331g",
            "thumbnail_url": "https://i.ytimg.com/vi/K0L_9Ln331g/hq720.jpg?sqp=-oaymwEcCNAFEJQDSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLA4fx7EBh3PgV9xek4rdTCr0LIB9Q"
        },
        {
            "link": "https://www.youtube.com/watch?v=ybt03airuTk",
            "thumbnail_url": "https://i.ytimg.com/vi/ybt03airuTk/hq720.jpg?sqp=-oaymwEcCNAFEJQDSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLBukg8LiYW3SnLbsH2nSwDvwhgE3w"
        },
        {
            "link": "https://www.youtube.com/watch?v=nbX2_wL8Bb8",
            "thumbnail_url": "https://i.ytimg.com/vi/nbX2_wL8Bb8/hq720.jpg?sqp=-oaymwEcCNAFEJQDSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLCgknpWi_ZlW28EufmTv9H6UD7e3w"
        },
        {
            "link": "https://www.youtube.com/watch?v=71m3SDGa220",
            "thumbnail_url": "https://i.ytimg.com/vi/71m3SDGa220/hq720.jpg?sqp=-oaymwEcCNAFEJQDSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLDqQIgCjWZ9vtiiIF5UGfJYRVkuCA"
        }
    ],
    "article_average": 2.8333333333333335,
    "customer_average": 4.6
}

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
 
