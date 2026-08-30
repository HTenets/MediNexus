"""Round-trip tests for the memory tiers.

The pre-existing memory tests only asserted graceful degradation (empty
results without Redis/DB). These assert the tiers actually store and return
data through their in-process stores, so the tiers can't silently regress to
no-ops.
"""

import pytest

from memory.manager import MemoryManager
from memory.working import SESSION_PREFIX, WorkingMemory


class TestWorkingMemoryRoundTrip:
    @pytest.mark.asyncio
    async def test_session_prefix(self):
        assert SESSION_PREFIX == "session:"

    @pytest.mark.asyncio
    async def test_agent_and_context_round_trip(self):
        wm = WorkingMemory()

        assert await wm.set_current_agent("s1", "doctor") is True
        assert await wm.get_current_agent("s1") == "doctor"

        assert await wm.set_context("s1", {"department": "内科"}) is True
        assert await wm.get_context("s1") == {"department": "内科"}

    @pytest.mark.asyncio
    async def test_update_context_merges(self):
        wm = WorkingMemory()
        await wm.set_context("s1", {"department": "内科"})

        merged = await wm.update_context("s1", {"urgency": "routine"})

        assert merged == {"department": "内科", "urgency": "routine"}
        assert await wm.get_context("s1") == merged

    @pytest.mark.asyncio
    async def test_session_lifecycle(self):
        wm = WorkingMemory()
        assert await wm.session_exists("s1") is False

        await wm.set_current_agent("s1", "triage")
        assert await wm.session_exists("s1") is True

        assert await wm.delete_session("s1") is True
        assert await wm.session_exists("s1") is False

    @pytest.mark.asyncio
    async def test_unknown_session_returns_defaults(self):
        wm = WorkingMemory()
        assert await wm.get_current_agent("nope") is None
        assert await wm.get_context("nope") == {}


class TestSemanticMemoryRoundTrip:
    @pytest.mark.asyncio
    async def test_add_and_read_allergy(self):
        mm = MemoryManager()

        assert await mm.store("patient_rt", "allergy", {"name": "青霉素过敏"}) is True
        assert await mm.semantic.get_allergies("patient_rt") == ["青霉素过敏"]

    @pytest.mark.asyncio
    async def test_add_condition_and_format_profile(self):
        mm = MemoryManager()
        await mm.store("patient_rt2", "allergy", {"name": "磺胺类过敏"})
        await mm.store("patient_rt2", "condition", {"name": "2型糖尿病"})

        profile = await mm.semantic.get_profile("patient_rt2")

        assert profile["allergies"] == ["磺胺类过敏"]
        assert profile["medical_history"] == ["2型糖尿病"]

        text = await mm.semantic.format_profile("patient_rt2")
        assert "磺胺类过敏" in text
        assert "2型糖尿病" in text

    @pytest.mark.asyncio
    async def test_duplicate_facts_are_not_repeated(self):
        mm = MemoryManager()
        await mm.semantic.add_history("patient_dup", "allergy", "青霉素过敏")
        await mm.semantic.add_history("patient_dup", "allergy", "青霉素过敏")

        assert await mm.semantic.get_allergies("patient_dup") == ["青霉素过敏"]

    @pytest.mark.asyncio
    async def test_unknown_memory_type_rejected(self):
        mm = MemoryManager()
        assert await mm.semantic.add_history("p", "not_a_kind", {"name": "x"}) is False


class TestEpisodicMemoryRoundTrip:
    @pytest.mark.asyncio
    async def test_store_then_recall(self):
        mm = MemoryManager()

        assert await mm.store_consultation(
            "patient_ep", "consult_1", assessment="急性上呼吸道感染"
        ) is True
        assert await mm.store_consultation(
            "patient_ep", "consult_2", assessment="急性支气管炎"
        ) is True

        episodes = await mm.episodic.recall("patient_ep")
        # Newest first
        assert [e["assessment"] for e in episodes][:2] == [
            "急性支气管炎",
            "急性上呼吸道感染",
        ]

    @pytest.mark.asyncio
    async def test_recall_respects_limit(self):
        mm = MemoryManager()
        for i in range(5):
            await mm.store_consultation(f"patient_lim{i}", f"c{i}", assessment=f"诊断{i}")
            await mm.store_consultation("patient_lim", f"c{i}", assessment=f"诊断{i}")

        assert len(await mm.episodic.recall("patient_lim", limit=2)) == 2

    @pytest.mark.asyncio
    async def test_format_recall_returns_readable_block(self):
        mm = MemoryManager()
        await mm.store_consultation("patient_fmt", "c1", assessment="感冒")

        text = await mm.episodic.format_recall("patient_fmt")

        assert "感冒" in text


class TestMemoryManagerComposition:
    @pytest.mark.asyncio
    async def test_retrieve_combines_profile_and_episodes(self):
        mm = MemoryManager()
        await mm.semantic.add_history("patient_all", "allergy", "青霉素过敏")
        await mm.store_consultation("patient_all", "c1", assessment="上呼吸道感染")

        block = await mm.retrieve("patient_all", "咳嗽")

        assert "患者长期档案" in block
        assert "既往就诊记录" in block
        assert "青霉素过敏" in block
        assert "上呼吸道感染" in block

    @pytest.mark.asyncio
    async def test_retrieve_empty_for_unknown_patient(self):
        mm = MemoryManager()
        assert await mm.retrieve("patient_unknown_xyz", "咳嗽") == ""

    @pytest.mark.asyncio
    async def test_retrieve_handles_blank_patient(self):
        mm = MemoryManager()
        assert await mm.retrieve("", "咳嗽") == ""
