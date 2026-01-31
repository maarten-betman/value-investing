import json
from typing import Any

import redis.asyncio as redis

from app.config import settings

_redis_client: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


async def cache_get(key: str) -> Any | None:
    r = await get_redis()
    value = await r.get(key)
    if value is not None:
        return json.loads(value)
    return None


async def cache_set(key: str, value: Any, ttl_seconds: int = 86400) -> None:
    r = await get_redis()
    await r.set(key, json.dumps(value, default=str), ex=ttl_seconds)


async def cache_delete(pattern: str) -> None:
    r = await get_redis()
    async for key in r.scan_iter(match=pattern):
        await r.delete(key)


async def close_redis() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
