import aioredis
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

# Global Redis connection
redis_client: Optional[aioredis.Redis] = None


async def init_redis():
    """Initialize Redis connection"""
    global redis_client
    try:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            retry_on_timeout=True,
            health_check_interval=30
        )
        # Test connection
        await redis_client.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.error(f"Error connecting to Redis: {e}")
        raise


async def get_redis() -> aioredis.Redis:
    """Get Redis client"""
    if redis_client is None:
        await init_redis()
    return redis_client


async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
        logger.info("Redis connection closed")
