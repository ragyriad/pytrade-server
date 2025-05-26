import redis
import json
from typing import Optional

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


def get_from_redis(key: str) -> Optional[dict]:
    value = redis_client.get(key)
    return json.loads(value) if value else None


def set_to_redis(key: str, value: dict, expiry: int = 86400):
    if value is not None:
        redis_client.setex(key, expiry, json.dumps(value))
    else:
        print("Value is None, not setting to redis")
        return None


def delete_from_redis(key: str):
    redis_client.delete(key)
