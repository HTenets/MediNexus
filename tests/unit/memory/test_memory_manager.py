"""Tests for MemoryManager — orchestrates all memory tiers."""

import pytest

pytestmark = pytest.mark.slow

from memory.manager import MemoryManager


class TestMemoryManager:
    """MemoryManager integration (without Redis/DB, graceful degradation)."""

    def setup_method(self):
        self.mm = MemoryManager()

    @pytest.mark.asyncio
    async def test_retrieve_empty(self):
        """Without DB, retrieve returns empty."""
        result = await self.mm.retrieve("nonexistent")
        assert result == ""

    @pytest.mark.asyncio
    async def test_retrieve_with_query(self):
        result = await self.mm.retrieve("nonexistent", "cough")
        assert result == ""

    @pytest.mark.asyncio
    async def test_store_consultation(self):
        result = await self.mm.store_consultation(
            patient_id="test",
            consultation_id="test_cons",
            assessment="感冒",
        )
        # Without DB, returns False gracefully
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_session_operations(self):
        """Session operations should not crash without Redis."""
        result = await self.mm.set_current_agent("s1", "doctor")
        assert isinstance(result, bool)

        agent = await self.mm.get_current_agent("s1")
        assert agent is None or agent == "doctor"

        exists = await self.mm.session_exists("s1")
        assert isinstance(exists, bool)

        ctx = await self.mm.get_context("s1")
        assert isinstance(ctx, dict)

        updated = await self.mm.update_context("s1", {"key": "val"})
        assert isinstance(updated, dict)
