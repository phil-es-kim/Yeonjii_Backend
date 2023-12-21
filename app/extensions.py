# extensions.py
import redis
import os

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
redis_client = redis.Redis.from_url(redis_url)

