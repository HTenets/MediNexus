"""Working memory (tier 1) — short-lived, per-session consultation state.

Backed by Redis when ``REDIS_URL`` is configured, otherwise by an in-process
dict. The in-process store is a *real* store, not a no-op: a single-worker
deployment without Redis still gets working memory, it just isn't shared across
workers and doesn't survive a restart.
"""

import logging
from typing import Any

from memory import _redis

logger = logging.getLogger(__name__)

SESSION_PREFIX = "session:"

#: Sessions are transient working state — 1 hour matches the supervisor TTL.
DEFAULT_TTL = 3600


class WorkingMemory:
    """Per-session scratch space: current agent, accumulated context."""

    def __init__(self, ttl: int = DEFAULT_TTL):
        self.ttl = ttl
        self._local: dict[str, Any] = {}

    # ── Raw key/value API ─────────────────────────────────────────────── #
    # Kept for callers that need an arbitrary blob rather than session state.

    async def get(self, key: str) -> Any | None:
        value = await _redis.redis_get(key)
        if value is not None:
            return value
        return self._local.get(key)

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        if await _redis.redis_set(key, value, ttl or self.ttl):
            return
        self._local[key] = value

    async def delete(self, key: str) -> bool:
        removed_local = self._local.pop(key, None) is not None
        return await _redis.redis_delete(key) or removed_local

    # ── Session-scoped API ────────────────────────────────────────────── #

    def _key(self, session_id: str) -> str:
        return f"{SESSION_PREFIX}{session_id}"

    async def _read_session(self, session_id: str) -> dict:
        data = await _redis.redis_get(self._key(session_id))
        if isinstance(data, dict):
            return data
        return dict(self._local.get(self._key(session_id)) or {})

    async def _write_session(self, session_id: str, data: dict) -> bool:
        if await _redis.redis_set(self._key(session_id), data, self.ttl):
            return True
        self._local[self._key(session_id)] = data
        return True

    async def set_current_agent(self, session_id: str, agent: str) -> bool:
        data = await self._read_session(session_id)
        data["current_agent"] = agent
        return await self._write_session(session_id, data)

    async def get_current_agent(self, session_id: str) -> str | None:
        data = await self._read_session(session_id)
        return data.get("current_agent")

    async def set_context(self, session_id: str, context: dict) -> bool:
        data = await self._read_session(session_id)
        data["context"] = dict(context or {})
        return await self._write_session(session_id, data)

    async def get_context(self, session_id: str) -> dict:
        data = await self._read_session(session_id)
        context = data.get("context")
        return context if isinstance(context, dict) else {}

    async def update_context(self, session_id: str, patch: dict) -> dict:
        """Merge ``patch`` into the session context and return the result."""
        data = await self._read_session(session_id)
        context = data.get("context")
        context = dict(context) if isinstance(context, dict) else {}
        context.update(patch or {})
        data["context"] = context
        await self._write_session(session_id, data)
        return context

    async def session_exists(self, session_id: str) -> bool:
        if await _redis.redis_exists(self._key(session_id)):
            return True
        return self._key(session_id) in self._local

    async def delete_session(self, session_id: str) -> bool:
        return await self.delete(self._key(session_id))
