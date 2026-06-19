"""Tests for WorkingMemory — Redis-backed session state.

These tests assume Redis is not running, so they verify graceful failure modes.
"""

import pytest

pytestmark = pytest.mark.slow

from memory.working import WorkingMemory


class TestWorkingMemory:
    """WorkingMemory without Redis (returns None/empty gracefully)."""

    def setup_method(self):
        self.memory = WorkingMemory()

    @pytest.mark.asyncio
    async def test_set_get_current_agent(self):
        """Without Redis, should return None gracefully (not crash)."""
        result = await self.memory.set_current_agent("test_session", "triage")
        assert isinstance(result, bool)

        agent = await self.memory.get_current_agent("test_session")
        # If Redis not available, get returns None
        assert agent is None or agent == "triage"

    @pytest.mark.asyncio
    async def test_set_get_context(self):
        """Without Redis, context operations should not crash."""
        result = await self.memory.set_context("test_session", {"department": "内科"})
        assert isinstance(result, bool)

        ctx = await self.memory.get_context("test_session")
        assert isinstance(ctx, dict)

    @pytest.mark.asyncio
    async def test_update_context(self):
        ctx = await self.memory.update_context("test_session", {"urgency": "routine"})
        assert isinstance(ctx, dict)

    @pytest.mark.asyncio
    async def test_session_exists(self):
        exists = await self.memory.session_exists("nonexistent")
        assert isinstance(exists, bool)

    @pytest.mark.asyncio
    async def test_delete_session(self):
        result = await self.memory.delete_session("test_session")
        assert isinstance(result, bool)


class TestWorkingMemoryUnit:
    """Lightweight unit tests that don't require Redis."""

    def test_session_prefix(self):
        from memory.working import SESSION_PREFIX
        assert SESSION_PREFIX == "session:"
