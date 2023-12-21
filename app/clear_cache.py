# clear_cache.py
import redis
import os
from dotenv import load_dotenv

def clear_redis_cache():
    # Load environment variables
    load_dotenv()

    # Set up Redis connection
    redis_url = os.getenv('REDIS_URL')
    redis_client = redis.Redis.from_url(redis_url)

    # Clear the entire Redis cache
    redis_client.flushall()
    print("Redis cache cleared successfully.")

if __name__ == '__main__':
    # You can add additional confirmation or security checks here
    confirm = input("Are you sure you want to clear the entire Redis cache? (yes/no): ")
    if confirm.lower() == 'yes':
        clear_redis_cache()
    else:
        print("Cache clear cancelled.")
