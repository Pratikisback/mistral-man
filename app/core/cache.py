import redis
import hashlib
import json
from dotenv import load_dotenv
import os
r = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=6379
)

def get_cache_key(query):
    return "rag:" + hashlib.md5(query.encode()).hexdigest()


def get_cached_answer(query):
    key = get_cache_key(query)
    value = r.get(key)
    if value:
        return json.loads(value)
    return None


def set_cached_answer(query, answer):
    key = get_cache_key(query)
    r.setex(key, 3600, json.dumps(answer))  