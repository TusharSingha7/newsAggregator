
from typing import AsyncGenerator
from fastapi import HTTPException
from config.config import settings
import logging
import redis.asyncio as aioredis
from sentence_transformers import SentenceTransformer


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisClient:
    redis: aioredis.Redis | None = None
    
    @classmethod
    async def connect(cls):
        try:
            logger.info("connecting... to redis")
            cls.redis = aioredis.from_url(
                url=settings.redis_url,
                encoding="utf-8",
                decode_responses = True,
                health_check_interval=30
            )
            await cls.redis.ping()
        except Exception as e:
            logger.error(f"failed connection to redis {e}")
        
    async def close(cls):
        if cls.redis:
            logger.info("closing Redis connection...")
            await cls.redis.close()
    
redis_client = RedisClient()

class Transformer:
    model: SentenceTransformer | None = None
    
    @classmethod
    async def load_model(cls):
        logger.info("Loading model all-MiniLM-L6-v2 from sentence transformer")
        cls.model = SentenceTransformer('all-MiniLM-L6-v2')
        
model_client = Transformer()

async def get_redis_client() -> AsyncGenerator[aioredis.Redis , None] :
    if redis_client.redis is None:
        raise HTTPException(status_code=503,detail="Redis connection not available")
    yield redis_client.redis
    
def get_model() -> SentenceTransformer :
    if Transformer.model is None:
        raise HTTPException(status_code=503,detail="model all-MiniLM-L6-v2 from sentence transformer failed")
    return Transformer.model

