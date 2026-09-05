import logging

import redis

from app.core.config import settings


logger = logging.getLogger(__name__)
cache_url = settings.REDIS_URL or settings.VALKEY_URL
redis_client = redis.Redis.from_url(cache_url, decode_responses=True)


def check_redis() -> bool:
    try:
        redis_client.ping()
        return True
    except redis.exceptions.RedisError as error:
        logger.warning("Valkey unavailable: %s", error)
        return False


def close_redis() -> None:
    redis_client.close()
