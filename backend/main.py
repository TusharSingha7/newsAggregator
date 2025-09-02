from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException
from config.config import settings
from fastapi.middleware.cors import CORSMiddleware
from utils.utils import redis_client, get_redis_client, model_client
from sklearn.metrics.pairwise import cosine_similarity
from config.config import UserData, NewsInstance
from tools.tools import fetchNews
import logging
import sys
import redis.asyncio as aioredis
import numpy as np
import json
from utils.utils import update_cache

# logger setup

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

# env

NEWS_API_KEY = settings.news_api_key


# lifecylce manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:

        await redis_client.connect()

        # verifying the connection
        await redis_client.redis.ping()

        logger.info("Redis connection established")

        logger.info("loading model")

        await model_client.load_model()

        logger.info("model loaded")

    except Exception as e:
        logger.critical(f"couldnt connect to redis : {e}")
        sys.exit(1)  # exiting the process with status code

    yield

    logger.info("App is shutting down")

    if redis_client.redis:
        await redis_client.close()
        logger.info("Redis connection closed")


# initialized fast instance
app = FastAPI(lifespan=lifespan)

# allowed origins
origins = [
    "http://localhost:3000",
    "http://localhost",
    "https://best-news-recom.vercel.app",
    "https://best-news-aggregator.vercel.app",
]

# adding cors middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API endpoints starts from here


@app.get(
    "/top-headlines",
    response_model=list[NewsInstance] | None,
    dependencies=[Depends(update_cache)],
)
async def topHeadlines(redis: aioredis.Redis = Depends(get_redis_client)):
    REDIS_KEY = "top-headlines"
    json_string = await redis.get(REDIS_KEY)
    articles: list[NewsInstance] = []

    if json_string:
        list_of_dict = json.loads(json_string)
        articles = [NewsInstance.model_validate(instance) for instance in list_of_dict]

    logger.info(f"headlines_length {len(articles)}")

    return articles


@app.get(
    "/top-headlines/{category}",
    response_model=list[NewsInstance] | None,
    dependencies=[Depends(update_cache)],
)
async def topCategoryHeadlines(category: str):
    url = f"https://newsapi.org/v2/top-headlines?country=us&category={category}&apiKey={NEWS_API_KEY}"
    if category not in [
        "business",
        "entertainment",
        "general",
        "health",
        "science",
        "sports",
        "technology",
    ]:
        return None
    top_headlines = await fetchNews(url=url)
    return top_headlines.articles


@app.get(
    "/top-headlines/sources/{source}",
    response_model=list[NewsInstance] | None,
    dependencies=[Depends(update_cache)],
)
async def topSourceHeadlines(sources: str):
    url = (
        f"https://newsapi.org/v2/top-headlines?sources={sources}&apiKey={NEWS_API_KEY}"
    )
    top_headlines = await fetchNews(url)
    return top_headlines.articles


@app.get(
    "/everything/{topic}",
    response_model=list[NewsInstance] | None,
    dependencies=[Depends(update_cache)],
)
async def everything(topic: str):
    url = f"https://newsapi.org/v2/everything?q={topic}&apiKey={NEWS_API_KEY}"
    all_news = await fetchNews(url=url)
    return all_news.articles


@app.get(
    "/everything",
    response_model=list[NewsInstance] | None,
    dependencies=[Depends(update_cache)],
)
async def defaultRoute(userId: str, redis: aioredis.Redis = Depends(get_redis_client)):
    # resort and return
    REDIS_KEY = "mix-headlines"
    json_string = await redis.get(REDIS_KEY)
    articles: list[NewsInstance] = []
    embeddings: list[float] = []

    if json_string:
        list_of_dict = json.loads(json_string)
        for item in list_of_dict:
            article = NewsInstance.model_validate(item)
            articles.append(article)
            embeddings.append(article.embedding)
    try:
        # perform cosine and sort

        user_embed_json_strings = await redis.lrange(userId, 0, 9)

        user_embeddings = [json.loads(item) for item in user_embed_json_strings]

        similarities = cosine_similarity(user_embeddings, embeddings)

        average_scores = np.mean(similarities, axis=0)

        paired_articles = list(zip(articles, average_scores))

        sorted_pair = sorted(paired_articles, key=lambda x: x[1], reverse=True)

        sorted_articles = [instance for instance, score in sorted_pair]
        
        logger.info(f"mix length {len(sorted_articles)}")

        return sorted_articles

    except Exception as e:
        logger.error(f"{e}")
        return articles


@app.post("/store", dependencies=[Depends(update_cache)], status_code=201)
async def embed_store(
    payload: UserData, redis: aioredis.Redis = Depends(get_redis_client)
):
    if len(payload.embedding) == 0:
        return {"message": "invalid embedding"}

    try:
        REDIS_KEY = payload.userId

        json_string = json.dumps(payload.embedding)

        # pipeline to send multiple commands together

        pipe = redis.pipeline()
        pipe.lpush(REDIS_KEY, json_string)
        pipe.ltrim(REDIS_KEY, 0, 9)
        await pipe.execute()

        return {"message": "data stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="embed upload failed")
