import hashlib
import json

import redis.asyncio as redis

from app.config import settings

_redis=redis.from_url(settings.redis_url)

TTL_SECONDS=3600

def _cache_key(prefix:str, *parts:str)->str:
    raw="|".join(parts)
    digest=hashlib.sha256(raw.encode()).hexdigest()[:16]
    return f"{prefix}:{digest}"

async def get_cached(prefix:str,*parts:str)->dict|None:
    try:
        key=_cache_key(prefix,*parts)
        raw=await _redis.get(key)
        return json.loads(raw) if raw else None
    except Exception:
        return None

async def set_cached(prefix:str,*parts:str,value:dict)->None:
    try:
        key=_cache_key(prefix,*parts)
        await _redis.set(key,json.dumps(value), ex=TTL_SECONDS)
    except Exception:
        pass