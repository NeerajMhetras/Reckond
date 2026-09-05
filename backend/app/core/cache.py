import json
import logging

import redis

from app.core.redis import redis_client


logger = logging.getLogger(__name__)


class JsonCache:
    def get(self, key: str):
        try:
            value = redis_client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except (redis.exceptions.RedisError, json.JSONDecodeError) as error:
            logger.warning("Valkey cache read failed key=%s: %s", key, error)
            return None

    def set(self, key: str, value, ttl: int) -> bool:
        try:
            redis_client.setex(key, ttl, json.dumps(value))
            return True
        except (redis.exceptions.RedisError, TypeError, ValueError) as error:
            logger.warning("Valkey cache write failed key=%s: %s", key, error)
            return False

    def delete(self, key: str) -> bool:
        try:
            redis_client.delete(key)
            return True
        except redis.exceptions.RedisError as error:
            logger.warning("Valkey cache invalidation failed key=%s: %s", key, error)
            return False


cache = JsonCache()


def recommendation_cache_key(user_id: int) -> str:
    return f"recommendations:v1:user:{user_id}"
