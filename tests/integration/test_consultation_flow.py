"""Integration tests for the full consultation flow — TriageAgent → SupervisorAgent → handover."""

import pytest
from agents.base import BaseAgent
from agents.registry import registry
from app.schemas.agent import HandoverManifest
from agents.triage.agent import TriageAgent
from orchestration.supervisor import SupervisorAgent
from orchestration.state import SessionState


# Register mock agents needed for full-flow routing tests
class _MockDoctor(BaseAgent):
    def __init__(self):
        super().__init__("doctor")
    async def run(self, context):
        return HandoverManifest(facts=["Mock doctor assessment"])

registry.register(_MockDoctor)


class TestTriageAgent:
    """TriageAgent evaluates symptoms and produces triage results."""

    @pytest.mark.asyncio
    async def test_keyword_triage_routine(self):
        agent = TriageAgent()
        manifest = await agent.run({"symptoms": "I have a mild headache for 2 days"})

        assert len(manifest.facts) > 0
        assert any("routine" in f.lower() or "urgency" in f.lower() for f in manifest.facts)
        assert manifest.evidence_level == "C"
        # Routine cases should not have risk flags
        assert "EMERGENCY_DETECTED" not in manifest.risk_flags

    @pytest.mark.asyncio
    async def test_keyword_triage_emergency(self):
        """Emergency keywords should trigger risk_flags."""
        agent = TriageAgent()
        manifest = await agent.run({"symptoms": "chest pain and difficulty breathing"})

        risk_text = " ".join(manifest.risk_flags).lower()
        assert "emergency" in risk_text
        assert manifest.context.get("urgency") == "emergency"

    @pytest.mark.asyncio
    async def test_keyword_triage_urgent(self):
        agent = TriageAgent()
        manifest = await agent.run({"symptoms": "high fever for 3 days, severe pain"})

        risk_text = " ".join(manifest.risk_flags).lower()
        assert "urgent" in risk_text
        assert manifest.context.get("urgency") == "urgent"

    @pytest.mark.asyncio
    async def test_department_detection_internal_medicine(self):
        agent = TriageAgent()
        manifest = await agent.run({"symptoms": "cough, fever, and sore throat"})

        dept = manifest.context.get("department", "")
        assert "internal_medicine" in dept

    @pytest.mark.asyncio
    async def test_department_detection_dermatology(self):
        agent = TriageAgent()
        manifest = await agent.run({"symptoms": "red rash on arms, itchy"})

        dept = manifest.context.get("department", "")
        assert "dermatology" in dept

    @pytest.mark.asyncio
    async def test_department_detection_mental_health(self):
        agent = TriageAgent()
        manifest = await agent.run({"symptoms": "feeling anxious and depressed, trouble sleeping"})

        dept = manifest.context.get("department", "")
        assert "mental_health" in dept

    @pytest.mark.asyncio
    async def test_bilingual_chinese_symptoms(self):
        agent = TriageAgent()
        manifest = await agent.run({"symptoms": "我头痛两天了"})

        assert len(manifest.facts) > 0
        dept = manifest.context.get("department", "")
        # headache maps to internal_medicine
        assert "internal_medicine" in dept

    @pytest.mark.asyncio
    async def test_keyword_triage_with_history(self):
        agent = TriageAgent()
        manifest = await agent.run({
            "symptoms": "stomach pain",
            "patient_history": "history of gastritis",
        })

        assert any("history" in f.lower() for f in manifest.facts)
        dept = manifest.context.get("department", "")
        assert "internal_medicine" in dept


class TestSupervisorAgent:
    """SupervisorAgent manages sessions and routes between agents."""

    @pytest.mark.asyncio
    async def test_create_session(self):
        supervisor = SupervisorAgent()
        session = await supervisor.create_session("test_id", "patient_01")

        assert session.session_id == "test_id"
        assert session.patient_id == "patient_01"
        assert session.current_agent == "triage"
        assert session.history == []

    @pytest.mark.asyncio
    async def test_get_session(self):
        supervisor = SupervisorAgent()
        await supervisor.create_session("session_abc", "patient_01")

        session = supervisor.get_session("session_abc")
        assert session is not None
        assert session.session_id == "session_abc"

    @pytest.mark.asyncio
    async def test_get_nonexistent_session(self):
        supervisor = SupervisorAgent()
        session = supervisor.get_session("nonexistent")
        assert session is None

    @pytest.mark.asyncio
    async def test_run_agent_updates_history(self):
        supervisor = SupervisorAgent()
        session = await supervisor.create_session("hist_test", "patient_01")

        manifest = await supervisor.run_agent(session, "I have a headache")

        assert len(session.history) == 2  # user msg + agent response
        assert session.history[0]["role"] == "user"
        assert session.history[1]["role"] == "agent"

    @pytest.mark.asyncio
    async def test_triage_to_doctor_routing(self):
        """After triage, the session should route to doctor."""
        supervisor = SupervisorAgent()
        session = await supervisor.create_session("route_test", "patient_01")

        await supervisor.run_agent(session, "mild headache")
        # triage should route to doctor by default
        assert session.current_agent == "doctor"


class TestFullConsultationFlow:
    """End-to-end consultation flow: triage → routing → handover."""

    @pytest.mark.asyncio
    async def test_triage_then_doctor_routing(self):
        """Simulate a complete triage step with routing."""
        supervisor = SupervisorAgent()
        session = await supervisor.create_session("full_test", "patient_01")

        assert session.current_agent == "triage"

        # Step 1: Triage
        triage_manifest = await supervisor.run_agent(session, "cough and fever for 3 days")
        assert triage_manifest is not None
        assert len(triage_manifest.facts) > 0

        # Should route to doctor
        assert session.current_agent == "doctor"

        # Context should contain triage results
        dept = session.context.get("department", "")
        assert "internal_medicine" in dept

    @pytest.mark.asyncio
    async def test_emergency_routing(self):
        """Emergency symptoms should set risk_flags and maintain triage as current agent."""
        supervisor = SupervisorAgent()
        session = await supervisor.create_session("emergency_test", "patient_01")

        manifest = await supervisor.run_agent(session, "chest pain")
        assert "EMERGENCY_DETECTED" in manifest.risk_flags

    @pytest.mark.asyncio
    async def test_session_history_accumulates(self):
        """Session history should grow with each interaction."""
        supervisor = SupervisorAgent()
        session = await supervisor.create_session("history_test", "patient_01")

        await supervisor.run_agent(session, "I have a headache")
        assert len(session.history) == 2

        # Second interaction
        await supervisor.run_agent(session, "It's been 3 days")
        assert len(session.history) == 4  # 2 per interaction
