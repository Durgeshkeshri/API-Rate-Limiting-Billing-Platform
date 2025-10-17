import redis
from app.config import settings

_pool = None

def get_redis():
    global _pool
    if _pool is None:
        _pool = redis.ConnectionPool.from_url(settings.REDIS_URL, decode_responses=True)
    return redis.Redis(connection_pool=_pool)

def check_redis_connection():
    try:
        client = get_redis()
        client.ping()
        return True
    except Exception:
        return False
