from typing import LiteralString
from pydantic import ValidationError
from config.config import NewsApiResponse, NewsInstance
from sentence_transformers import SentenceTransformer
from fastapi import HTTPException
import httpx
import logging
import json
import redis.asyncio as aioredis
import asyncio
from config.config import settings

NEWS_API_KEY = settings.news_api_key

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


async def fetchNews(url: LiteralString) -> NewsApiResponse | None:

    client: httpx.AsyncClient = httpx.AsyncClient()

    try:
        response = await client.get(url=url)
        response.raise_for_status()
        response_json = response.json()
        return NewsApiResponse(**response_json)

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "Message": "Api Call Failed ",
                "Error": f"network error : {str(exc)}",
            },
        )

    except ValidationError as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "Message": " Failed to validate the news response ",
                "Error": exc.errors(),
            },
        )

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail={
                "message": "failed api call with bad status code",
                "error": f"received status code : {exc.response.status_code}",
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=404, detail={"Message": "Api Call Failed ", "Error": str(e)}
        )


async def get_embedded_articles(
    url: str, model: SentenceTransformer
) -> list[NewsInstance]:

    try:
        response: NewsApiResponse = await fetchNews(url=url)
        news_articles = response.articles

        if len(news_articles) > 200:
            news_articles = news_articles[:200]

        sentences = []

        for article in news_articles:
            sentences.append(f"{article.title}{article.description}{article.content}")

        articles_embeddings = model.encode(sentences)

        for article, embeddings in zip(news_articles, articles_embeddings):
            article.embedding = embeddings.tolist()

        return news_articles
    except Exception as e:
        logger.error(f"error in get_embedded_articles {e}")
        return []


async def cache_filler(redis: aioredis.Redis, model: SentenceTransformer):

    logger.info("Background process started")

    REDIS_KEY_HEADLINES = "top-headlines"
    REDIS_KEY_MIXHEADLINES = "mix-headlines"

    try:
        # perform ML embedding conversion and caching here
        headlines_url = (
            f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
        )

        top_headlines_articles = await get_embedded_articles(
            url=headlines_url, model=model
        )

        # convert to dict and then to json to serialize
        list_of_dict = [
            article.model_dump(mode="json") for article in top_headlines_articles
        ]
        json_string = json.dumps(list_of_dict)

        # cache the news in redis

        await redis.set(REDIS_KEY_HEADLINES, json_string)

        # process for mix headlines

        for category in [
            "business",
            "entertainment",
            "general",
            "health",
            "science",
            "sports",
            "technology",
        ]:
            url = f"https://newsapi.org/v2/top-headlines?country=us&category={category}&apiKey={NEWS_API_KEY}"
            news_articles = await get_embedded_articles(url=url, model=model)
            top_headlines_articles.extend(news_articles)
            await asyncio.sleep(10)

        # convert the list to dict and then to json to be serializable
        mix_list_of_dict = [
            article.model_dump(mode="json") for article in top_headlines_articles
        ]
        mix_json_string = json.dumps(mix_list_of_dict)

        await redis.set(REDIS_KEY_MIXHEADLINES, mix_json_string)

    except httpx.RequestError as e:
        logger.error(f"api request error occured {e}")

    except Exception as e:
        logger.error(f"error occured while processing backgroud task {e}")

    await asyncio.sleep(10)
