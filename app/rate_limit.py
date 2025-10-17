import time
from app.redis_client import get_redis
from app.config import settings

def check_user_rate_limit(user_id: int) -> bool:
    key = f"user:{user_id}:requests"
    window = settings.API_RATE_WINDOW
    limit = settings.API_RATE_LIMIT
    now = int(time.time())
    r = get_redis()
    window_start = now - window
    r.zremrangebyscore(key, '-inf', window_start)
    current = r.zcount(key, window_start, now)
    if current >= limit:
        return False
    r.zadd(key, {str(now): now})
    r.expire(key, window+60)
    return True
