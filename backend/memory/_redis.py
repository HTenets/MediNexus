"""Lazy Redis accessor shared by the memory tiers.

Returns ``None`` when ``REDIS_URL`` is unset, the ``redis`` package is missing,
or a call fails — every tier then falls back to its in-process store instead of
crashing. The failure is latched so a broken Redis doesn't get retried on every
single memory operation.
"""

import json
import logging
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

_client = None
_unavailable = False


def get_redis():
    """Return a shared async Redis client, or None if Redis is not usable."""
    global _client, _unavailable

    if _unavailable:
        return None
    if _client is not None:
        return _client
    if not settings.redis_url:
        _unavailable = True
        return None

    try:
        import redis.asyncio as aioredis
    except ImportError:
        logger.warning("redis package not installed — memory tiers use in-process store")
        _unavailable = True
        return None

    try:
        _client = aioredis.from_url(settings.redis_url, decode_responses=True)
    except Exception as e:  # noqa: BLE001 - config errors must not kill startup
        logger.warning("Redis client init failed (%s) — using in-process store", e)
        _unavailable = True
        return None

    return _client


def _latch_failure(e: Exception, op: str) -> None:
    """Log a Redis failure. Connection drops are transient, so keep retrying."""
    logger.warning("Redis %s failed, using in-process fallback: %s", op, e)


async def redis_get(key: str) -> Any | None:
    client = get_redis()
    if client is None:
        return None
    try:
        raw = await client.get(key)
    except Exception as e:  # noqa: BLE001
        _latch_failure(e, "get")
        return None
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None


async def redis_set(key: str, value: Any, ttl: int | None = None) -> bool:
    client = get_redis()
    if client is None:
        return False
    try:
        payload = json.dumps(value, ensure_ascii=False, default=str)
        if ttl:
            await client.setex(key, ttl, payload)
        else:
            await client.set(key, payload)
        return True
    except Exception as e:  # noqa: BLE001
        _latch_failure(e, "set")
        return False


async def redis_delete(key: str) -> bool:
    client = get_redis()
    if client is None:
        return False
    try:
        return bool(await client.delete(key))
    except Exception as e:  # noqa: BLE001
        _latch_failure(e, "delete")
        return False


async def redis_exists(key: str) -> bool:
    client = get_redis()
    if client is None:
        return False
    try:
        return bool(await client.exists(key))
    except Exception as e:  # noqa: BLE001
        _latch_failure(e, "exists")
        return False
