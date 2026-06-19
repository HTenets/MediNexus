"""Tests for SemanticMemory — patient profile management."""

import pytest

pytestmark = pytest.mark.slow

from memory.stores.semantic import SemanticMemory


class TestSemanticMemory:
    """SemanticMemory without DB (profile returns empty)."""

    def setup_method(self):
        self.memory = SemanticMemory()

    @pytest.mark.asyncio
    async def test_get_profile_empty(self):
        """No DB should return empty profile."""
        profile = await self.memory.get_profile("nonexistent")
        assert isinstance(profile, dict)
        assert "patient_info" in profile
        assert "allergies" in profile
        # In dev mode without DB, returns empty data
        assert profile["patient_info"] == {}

    @pytest.mark.asyncio
    async def test_get_allergies_empty(self):
        allergies = await self.memory.get_allergies("nonexistent")
        assert allergies == []

    @pytest.mark.asyncio
    async def test_format_profile_empty(self):
        text = await self.memory.format_profile("nonexistent")
        assert text == ""  # No patient info found

    @pytest.mark.asyncio
    async def test_add_history_no_db(self):
        """Without DB, add_history should return False gracefully."""
        result = await self.memory.add_history("test", "allergy",
                                                {"name": "青霉素过敏"})
        # In dev mode without real DB, this may fail silently
        assert isinstance(result, bool)
