"""Tests for CoordinatorAgent — multi-specialty consultation."""

import pytest
from agents.coordinator.agent import CoordinatorAgent, COMPLEXITY_TRIGGERS
from agents.coordinator.consultation_protocol import (
    ConsultationPhase, SpecialistOpinion, ConsultationReport,
)


class TestCoordinatorAgent:
    """CoordinatorAgent manages multi-specialty consultations."""

    def setup_method(self):
        self.agent = CoordinatorAgent()

    @pytest.mark.asyncio
    async def test_simple_case_no_consultation(self):
        """A simple cold shouldn't need multi-specialty."""
        manifest = await self.agent.run({
            "symptoms": "I have a cold and cough for 2 days",
            "department": "internal_medicine",
        })
        # "cold cough" doesn't trigger any complexity keywords
        assert manifest is not None

    @pytest.mark.asyncio
    async def test_complex_case_triggers_specialties(self):
        """Skin + fever should trigger dermatology + internal medicine."""
        manifest = await self.agent.run({
            "symptoms": "fever and rash all over body with joint pain",
            "department": "dermatology",
        })
        assert manifest is not None
        context = manifest.context
        assert context.get("consultation_needed") is True
        assert "dermatology" in context.get("specialties_consulted", [])

    @pytest.mark.asyncio
    async def test_mental_physical_trigger(self):
        """Anxiety + chest pain should trigger mental + internal."""
        manifest = await self.agent.run({
            "symptoms": "chest pain and severe anxiety, trouble sleeping",
            "department": "mental_health",
        })
        specialties = manifest.context.get("specialties_consulted", [])
        assert "mental_health" in specialties

    @pytest.mark.asyncio
    async def test_empty_symptoms(self):
        """Empty symptoms shouldn't crash."""
        manifest = await self.agent.run({"symptoms": ""})
        assert manifest is not None

    @pytest.mark.asyncio
    async def test_urgent_case_risk_flags(self):
        """Urgent urgency should set risk flags."""
        manifest = await self.agent.run({
            "symptoms": "severe chest pain and difficulty breathing",
            "urgency": "emergency",
        })
        assert "EMERGENCY_DETECTED" in manifest.risk_flags


class TestComplexityAnalyzer:
    """Complexity trigger mapping."""

    def test_triggers_defined(self):
        """All triggers should have keywords + specialties + reason."""
        for name, trigger in COMPLEXITY_TRIGGERS.items():
            assert "keywords" in trigger, f"{name} missing keywords"
            assert "specialties" in trigger, f"{name} missing specialties"
            assert "reason" in trigger, f"{name} missing reason"
            assert len(trigger["keywords"]) > 0
            assert len(trigger["specialties"]) > 0

    def test_skin_systemic_triggers(self):
        """Skin + systemic should need derm + internal_medicine."""
        trigger = COMPLEXITY_TRIGGERS["skin_systemic"]
        assert "dermatology" in trigger["specialties"]
        assert "internal_medicine" in trigger["specialties"]

    def test_mental_physical_triggers(self):
        """Mental + physical should need mental_health + internal_medicine."""
        trigger = COMPLEXITY_TRIGGERS["mental_physical"]
        assert "mental_health" in trigger["specialties"]
        assert "internal_medicine" in trigger["specialties"]


class TestConsultationProtocol:
    """Data structures for multi-specialty consultation."""

    def test_specialist_opinion_defaults(self):
        op = SpecialistOpinion(specialty="internal_medicine")
        assert op.diagnosis == []
        assert op.confidence == 0.5
        assert op.evidence_level == "C"

    def test_consultation_report(self):
        report = ConsultationReport(
            session_id="s1", patient_id="p1",
            chief_complaint="chest pain and rash",
            specialties_involved=["internal_medicine", "dermatology"],
        )
        assert report.chief_complaint == "chest pain and rash"
        assert len(report.specialties_involved) == 2
        assert report.completed_at != ""

    def test_consultation_phases(self):
        """Verify all phases are defined."""
        assert ConsultationPhase.INIT == "init"
        assert ConsultationPhase.COMPLETED == "completed"


class TestCoordinatorIntegration:
    """Integration: coordinator with actual skills loaded."""

    @pytest.mark.asyncio
    async def test_invite_specialist(self):
        agent = CoordinatorAgent()
        result = await agent.invite_specialist("internal_medicine")
        assert result["status"] == "invited"
        assert result["skill_available"] is True

    @pytest.mark.asyncio
    async def test_invite_nonexistent_specialist(self):
        agent = CoordinatorAgent()
        result = await agent.invite_specialist("nonexistent")
        assert result["status"] == "not_found"
        assert result["skill_available"] is False
