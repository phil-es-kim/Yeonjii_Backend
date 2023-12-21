import redis
import os
from dotenv import load_dotenv

def check_redis_keys_contents():
    load_dotenv()
    # Load environment variables
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')

    # Set up Redis connection
    redis_client = redis.Redis.from_url(redis_url)

    # Retrieve all keys
    keys = redis_client.keys('*')
    print(f"Keys in Redis: {keys}")

    # Fetch and print contents of each key
    for key in keys:
        value = redis_client.get(key)
        print(f"Key: {key.decode('utf-8')}, Value: {value.decode('utf-8')}")

if __name__ == '__main__':
    check_redis_keys_contents()

