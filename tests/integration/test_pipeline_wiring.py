"""Integration tests for supervisor → memory / RAG / agent wiring.

These assert the "sold" capabilities actually participate at runtime, which
was the core v0.1.1 concern: the classes existed but were never connected.
"""

import pytest

from app.schemas.agent import HandoverManifest
from knowledge.factory import create_rag_query
from memory.manager import MemoryManager
from orchestration.state import SessionState
from orchestration.supervisor import SupervisorAgent


class RecordingAgent:
    """Agent that records the context it received."""

    instances: list["RecordingAgent"] = []

    def __init__(self):
        self.rag_query = None
        self.received = None
        RecordingAgent.instances.append(self)

    async def on_pre_process(self, context):
        self.received = context
        return context

    async def run(self, context):
        self.received = context
        return HandoverManifest(
            facts=["ok"],
            context={"assessment": "测试诊断", "next_agent": "complete"},
        )

    async def on_post_process(self, manifest):
        return manifest


@pytest.fixture(autouse=True)
def _clear():
    RecordingAgent.instances.clear()
    yield
    RecordingAgent.instances.clear()


def _supervisor(agent_map=None) -> SupervisorAgent:
    """Build a supervisor whose registry resolves our recording agent."""
    from agents.registry import registry

    sv = SupervisorAgent(memory=MemoryManager(), rag_query=create_rag_query())
    original = dict(registry._agents) if hasattr(registry, "_agents") else None
    for name in (agent_map or ["triage", "doctor", "review", "followup"]):
        registry._agents[name] = RecordingAgent
    sv._registry_backup = original
    return sv


class TestRAGInjection:
    @pytest.mark.asyncio
    async def test_agent_receives_shared_rag_query(self):
        sv = _supervisor()
        session = await sv.create_session("rag_sess", "patient_rag")

        await sv.run_agent(session, "咳嗽发热")

        agent = RecordingAgent.instances[-1]
        assert agent.rag_query is sv.rag_query
        assert agent.rag_query is not None

    @pytest.mark.asyncio
    async def test_agent_can_retrieve_through_injected_rag(self):
        """The injected stack must be functional, not just non-None."""
        sv = _supervisor()
        session = await sv.create_session("rag_sess2", "patient_rag2")

        await sv.run_agent(session, "咳嗽发热三天")

        agent = RecordingAgent.instances[-1]
        context = await agent.rag_query.query_formatted("咳嗽发热三天", top_k=3)
        assert "知识库检索结果" in context


class TestMemoryInjection:
    @pytest.mark.asyncio
    async def test_patient_memory_absent_for_new_patient(self):
        sv = _supervisor()
        session = await sv.create_session("mem_sess", "patient_new_xyz")

        await sv.run_agent(session, "头痛")

        agent = RecordingAgent.instances[-1]
        assert "patient_memory" not in agent.received

    @pytest.mark.asyncio
    async def test_patient_memory_injected_for_returning_patient(self):
        """A returning patient's stored profile must reach the agent."""
        sv = _supervisor()
        await sv.memory.semantic.add_history(
            "patient_returning", "allergy", {"name": "青霉素过敏"}
        )

        session = await sv.create_session("mem_sess2", "patient_returning")
        await sv.run_agent(session, "头痛")

        agent = RecordingAgent.instances[-1]
        assert "patient_memory" in agent.received
        assert "青霉素过敏" in agent.received["patient_memory"]

    @pytest.mark.asyncio
    async def test_completed_consultation_is_archived(self):
        sv = _supervisor()
        session = await sv.create_session("mem_sess3", "patient_archive")
        session.current_agent = "triage"

        # Force the pipeline to finish on the next step
        original_route = sv.route

        async def _to_complete(session, context):
            return "complete"

        sv.route = _to_complete
        try:
            await sv.run_agent(session, "咳嗽")
        finally:
            sv.route = original_route

        episodes = await sv.memory.episodic.recall("patient_archive")
        assert any(e["assessment"] == "测试诊断" for e in episodes)

    @pytest.mark.asyncio
    async def test_working_memory_tracks_current_agent(self):
        sv = _supervisor()
        session = await sv.create_session("mem_sess4", "patient_wm")

        await sv.run_agent(session, "咳嗽")

        assert await sv.memory.working.session_exists("mem_sess4") is True
        assert await sv.memory.get_current_agent("mem_sess4") is not None


class TestMemoryFailuresAreNonFatal:
    @pytest.mark.asyncio
    async def test_broken_memory_does_not_break_consultation(self):
        sv = _supervisor()

        class BrokenMemory:
            async def retrieve(self, patient_id, context=None):
                raise RuntimeError("memory down")

            async def set_current_agent(self, *a, **kw):
                raise RuntimeError("memory down")

            async def update_context(self, *a, **kw):
                raise RuntimeError("memory down")

            async def store_consultation(self, *a, **kw):
                raise RuntimeError("memory down")

        sv.memory = BrokenMemory()
        session = await sv.create_session("mem_broken", "patient_broken")

        manifest = await sv.run_agent(session, "咳嗽")

        assert manifest.facts == ["ok"]
        assert session.history, "history must still be recorded"
