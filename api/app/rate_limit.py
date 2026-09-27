import time

import redis.asyncio as redis

from app.config import settings

_redis=redis.from_url(settings.redis_url)

BUCKET_CAPACITY=10
REFILL_RATE=1

async def check_rate_limit(user_id:str) -> bool:
    key=f"ratelimit:{user_id}"
    now=time.time()

    data=await _redis.hgetall(key)
    if data:
        tokens=float(data[b"tokens"])
        last_refill=float(data[b"last_refill"])
    else:
        tokens=BUCKET_CAPACITY
        last_refill=now
    
    elapsed=now-last_refill
    tokens=min(BUCKET_CAPACITY, tokens+elapsed * REFILL_RATE)

    if tokens < 1:
        await _redis.hset(key, mapping={"tokens":tokens,"last_refill":now})
        return False

    tokens -= 1
    await _redis.hset(key,mapping={"tokens":tokens, "last_refill":now})
    await _redis.expire(key,3600)

    return True


