from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI , HTTPException
from typing import Optional , LiteralString 
from pydantic import BaseModel , Field , HttpUrl , ValidationError
from config.config import settings
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
from utils.utils import redis_client , get_redis_client , get_model , model_client
from sklearn.metrics.pairwise import cosine_similarity
import httpx
import logging 
import sys
import redis.asyncio as aioredis
import asyncio
import numpy as np
import json

# logger setup

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

# env 

NEWS_API_KEY = settings.news_api_key

# lifecylce manager 
@asynccontextmanager
async def lifespan(app : FastAPI):
    try :
        
        app.state.http_client = httpx.AsyncClient()

        logger.info("httpx client Initialized")

        await redis_client.connect()
        
        # verifying the connection
        await redis_client.redis.ping()
        
        logger.info("Redis connection established")
        
        logger.info("loading model")
        
        await model_client.load_model()
        
        logger.info("model loaded")
        
        task = asyncio.create_task(cache_filler(redis_client.redis))
        
        
    except Exception as e:
        logger.critical(f"couldnt connect to redis : {e}")
        sys.exit(1) # exiting the process with status code

    yield

    logger.info("App is shutting down")

    await app.state.http_client.aclose()

    logger.info("httpx client closed")
    
    if redis_client.redis:
        await redis_client.close()
        logger.info("Redis connection closed")
    
    task.cancel()
    
    try:
        await task
    
    except asyncio.CancelledError as e:
        logger.info("Background task successfully cancelled")

# initialized fast instance
app = FastAPI(lifespan=lifespan)

# allowed origins
origins = [
    "http://localhost:3000",
    "http://localhost",
    "https://best-news-recom.vercel.app",
    "https://best-news-aggregator.vercel.app"
]
# adding cors middleware 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#pydantic models for schema validation

class Source(BaseModel):
    id : str | None = None
    name : str

class NewsInstance(BaseModel):
    source : Source
    author : str | None = None
    title : str
    description : str | None = None
    url : HttpUrl | None = None
    urlToImage: HttpUrl | None = None
    publishedAt : str
    content : str | None = None
    embedding : Optional[list[float]] = None

class NewsApiResponse(BaseModel):
    status: str = Field(description="status of Api call")
    totalResults: int = Field(description="total count of returned news")
    articles : list[NewsInstance]
    
class UserData(BaseModel):
    userId : str = Field(description="unique user identification string")
    embedding : list[float] = Field(...,description="news embedding to store ")
    
async def get_embedded_articles(url : str ) -> list[NewsInstance] :
    
    model : SentenceTransformer = get_model()
    
    try:
        response : NewsApiResponse = await fetchNews(url=url)
        news_articles = response.articles
        
        if len(news_articles) > 200:
            news_articles = news_articles[:200]
        
        sentences = []
        
        for article in news_articles:
            sentences.append(f"{article.title}{article.description}{article.content}")
            
        articles_embeddings = model.encode(sentences)
        
        for article , embeddings in zip( news_articles , articles_embeddings):
            article.embedding = embeddings.tolist()
            
        return news_articles
    except Exception as e :
        logger.error(f"error in get_embedded_articles {e}")
        return []
    
async def cache_filler(redis : aioredis.Redis):
    
    logger.info("Background process started")
    
    REDIS_KEY_HEADLINES = "top-headlines"
    REDIS_KEY_MIXHEADLINES = "mix-headlines"
    
    while True:
        try:
            # perform ML embedding conversion and caching here 
            headlines_url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
            
            top_headlines_articles = await get_embedded_articles(url=headlines_url)
            
            # convert to dict and then to json to serialize
            list_of_dict = [article.model_dump(mode='json') for article in top_headlines_articles]
            json_string = json.dumps(list_of_dict)
            
            # cache the news in redis 
            
            await redis.set(REDIS_KEY_HEADLINES,json_string)  
            
            # process for mix headlines 
            
            for category in ["business" , "entertainment" , "general" , "health" , "science" , "sports" , "technology"]:
                url = f"https://newsapi.org/v2/top-headlines?country=us&category={category}&apiKey={NEWS_API_KEY}"
                news_articles = await get_embedded_articles(url=url)
                top_headlines_articles.extend(news_articles)
                await asyncio.sleep(10)
            
            # convert the list to dict and then to json to be serializable
            mix_list_of_dict = [article.model_dump(mode='json') for article in top_headlines_articles]
            mix_json_string = json.dumps(mix_list_of_dict)
            
            await redis.set(REDIS_KEY_MIXHEADLINES,mix_json_string)
            
        except httpx.RequestError as e:
            logger.error(f"api request error occured {e}")
            
        except Exception as e:
            logger.error(f"error occured while processing backgroud task {e}")
        
        await asyncio.sleep(10)

async def fetchNews(url : LiteralString) -> NewsApiResponse | None:

    client: httpx.AsyncClient = app.state.http_client

    try:
        response = await client.get(url=url)
        response.raise_for_status()
        response_json = response.json()
        return NewsApiResponse(**response_json)
    
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail= {
                "Message" : "Api Call Failed ",
                "Error" : f"network error : {str(exc)}",
            }
        )
    
    except ValidationError as exc:
        raise HTTPException(
            status_code=500,
            detail= {
                "Message" : " Failed to validate the news response ",
                "Error" : exc.errors()
            }
        )
        
    except httpx.HTTPStatusError as exc :
        raise HTTPException(
            status_code=exc.response.status_code,
            detail={
                "message" : "failed api call with bad status code",
                "error" : f"received status code : {exc.response.status_code}"
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail= {
                "Message" : "Api Call Failed ",
                "Error" : str(e)
            }
        )
        
# API endpoints starts from here 

@app.get('/top-headlines' , response_model=list[NewsInstance] | None)
async def topHeadlines(redis: aioredis.Redis = Depends(get_redis_client)):
    REDIS_KEY = "top-headlines"
    json_string = await redis.get(REDIS_KEY);
    articles : list[NewsInstance] = []
    
    if json_string:
        list_of_dict = json.loads(json_string)
        articles = [NewsInstance.model_validate(instance) for instance in list_of_dict]
        
    logger.info(f"headlines_length {len(articles)}")
    
    return articles

@app.get('/top-headlines/{category}' , response_model=list[NewsInstance] | None)
async def topCategoryHeadlines(category : str):
    url = f"https://newsapi.org/v2/top-headlines?country=us&category={category}&apiKey={NEWS_API_KEY}"
    if category not in ["business" , "entertainment" , "general" , "health" , "science" , "sports" , "technology"]:
        return None
    top_headlines = await fetchNews(url=url)
    return top_headlines.articles

@app.get('/top-headlines/sources/{source}' , response_model=list[NewsInstance] | None)
async def topSourceHeadlines(sources : str):
    url = f"https://newsapi.org/v2/top-headlines?sources={sources}&apiKey={NEWS_API_KEY}"
    top_headlines = await fetchNews(url)
    return top_headlines.articles

@app.get('/everything/{topic}' , response_model=list[NewsInstance] | None)
async def everything(topic : str):
    url = f"https://newsapi.org/v2/everything?q={topic}&apiKey={NEWS_API_KEY}"
    all_news = await fetchNews(url=url)
    return all_news.articles

@app.get('/everything' , response_model=list[NewsInstance] | None)
async def defaultRoute(userId : str ,redis: aioredis.Redis = Depends(get_redis_client)):
    # resort and return 
    REDIS_KEY = "mix-headlines"
    json_string = await redis.get(REDIS_KEY)
    articles : list[NewsInstance] = []
    embeddings : list[float] = []
    
    if json_string:
        list_of_dict = json.loads(json_string)
        for item in list_of_dict:
            article = NewsInstance.model_validate(item)
            articles.append(article)
            embeddings.append(article.embedding)
    try:
        # perform cosine and sort 
        
        user_embed_json_strings = await redis.lrange(userId,0,9)
        user_embeddings = [json.loads(item) for item in user_embed_json_strings]
        
        similarities = cosine_similarity(user_embeddings , embeddings)
        
        average_scores = np.mean(similarities , axis=0)
        
        paired_articles = list(zip(articles , average_scores))
        
        sorted_pair = sorted(paired_articles, key = lambda x:x[1], reverse = True)
        
        sorted_articles = [instance for instance , score in sorted_pair]
        
        logger.info(f"mix length {len(sorted_articles)}")
        return sorted_articles
    except Exception as e:
        logger.error(f"{e}")
        return articles
    
@app.post('/store' , status_code=201)
async def embed_store(
    payload : UserData,
    redis : aioredis.Redis = Depends(get_redis_client)
):
    if len(payload.embedding) == 0:
        return {"message" : "invalid embedding"}
    
    try:
        REDIS_KEY = payload.userId
        
        json_string = json.dumps(payload.embedding)
        
        # pipeline to send multiple commands together

        pipe = redis.pipeline()
        pipe.lpush(REDIS_KEY , json_string)
        pipe.ltrim(REDIS_KEY,0,9)
        await pipe.execute()
        
        return {
            "message" : "data stored successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="embed upload failed"
        )
        