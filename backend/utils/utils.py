from typing import AsyncGenerator
from fastapi import HTTPException , BackgroundTasks
from config.config import settings
import logging
import redis.asyncio as aioredis
from sentence_transformers import SentenceTransformer
import threading
import time
from tools.tools import cache_filler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RedisClient:
    redis: aioredis.Redis | None = None

    @classmethod
    async def connect(cls):
        try:
            if cls.redis is None:
                logger.info("connecting... to redis")
                cls.redis = aioredis.from_url(
                    url=settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    health_check_interval=30,
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
        cls.model = SentenceTransformer("all-MiniLM-L6-v2")


model_client = Transformer()


class CacheFiller:
    lock: threading.Lock = threading.Lock()
    last_time: float = 0.0

    @classmethod
    def fill_cache(cls , task : BackgroundTasks):

        with cls.lock:
            curr_time = time.time()
            # acquire lock and then proceed to avoid race conditions
            if curr_time - cls.last_time > 960:
                task.add_task(cache_filler,model=Transformer.model , redis=RedisClient.redis)
                cls.last_time = curr_time


cache_filler_client = CacheFiller()


async def get_redis_client() -> AsyncGenerator[aioredis.Redis, None]:
    if redis_client.redis is None:
        raise HTTPException(status_code=503, detail="Redis connection not available")
    yield redis_client.redis


def update_cache(task : BackgroundTasks):
    cache_filler_client.fill_cache(task=task)
