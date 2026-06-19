"""Tests for FollowupAgent — generates follow-up plans based on diagnosis."""

import pytest
from agents.followup.agent import FollowupAgent


class TestFollowupAgent:
    """FollowupAgent generates follow-up plans."""

    def setup_method(self):
        self.agent = FollowupAgent()

    @pytest.mark.asyncio
    async def test_followup_with_chronic_diagnosis(self):
        """Chronic diseases should generate multi-visit plans."""
        manifest = await self.agent.run({
            "symptoms": "headache for 1 month",
            "diagnosis": {"possible_diagnoses": [{"diagnosis": "高血压", "likelihood": "高"}]},
        })
        facts_text = " ".join(manifest.facts)
        assert "随访" in facts_text
        assert "30" in facts_text or "慢性" in facts_text

    @pytest.mark.asyncio
    async def test_followup_with_self_limiting(self):
        """Self-limiting conditions (cold) should not require long follow-up."""
        manifest = await self.agent.run({
            "symptoms": "cough for 2 days",
            "diagnosis": {"possible_diagnoses": [{"diagnosis": "感冒", "likelihood": "高"}]},
        })
        facts_text = " ".join(manifest.facts)
        assert "随访" in facts_text
        assert "警示" in facts_text

    @pytest.mark.asyncio
    async def test_followup_without_diagnosis(self):
        """No diagnosis should still produce a generic follow-up."""
        manifest = await self.agent.run({
            "symptoms": "test",
            "diagnosis": {},
        })
        assert len(manifest.facts) > 0
        assert "随访" in " ".join(manifest.facts)

    @pytest.mark.asyncio
    async def test_followup_has_pending_questions(self):
        """Follow-up should ask about medication adherence."""
        manifest = await self.agent.run({
            "symptoms": "cough",
            "diagnosis": {"possible_diagnoses": [{"diagnosis": "支气管炎"}]},
        })
        assert len(manifest.pending_questions) > 0

    @pytest.mark.asyncio
    async def test_followup_with_medications(self):
        """Treatment plan with medications should generate reminders."""
        manifest = await self.agent.run({
            "symptoms": "cough",
            "diagnosis": {
                "possible_diagnoses": [{"diagnosis": "支气管炎"}],
                "treatment_plan": {
                    "medications": [{"name": "阿莫西林", "dosage": "500mg tid"}],
                },
            },
        })
        facts_text = " ".join(manifest.facts)
        assert "用药" in facts_text or "阿莫西林" in facts_text

    @pytest.mark.asyncio
    async def test_schedule_method(self):
        """schedule() should return correct date offset."""
        result = await self.agent.schedule("patient_01", 14)
        assert result["patient_id"] == "patient_01"
        assert result["days_offset"] == 14


class TestFollowupScheduler:
    """Scheduler module."""

    def test_generate_schedule(self):
        from agents.followup.scheduler import generate_schedule, DEFAULT_PLANS
        schedule = generate_schedule("p1", "c1", "chronic_disease")
        plan = DEFAULT_PLANS["chronic_disease"]
        assert len(schedule) == plan.total_visits
        assert schedule[0].visit_number == 1
        assert schedule[-1].visit_number == plan.total_visits

    def test_generate_schedule_routine(self):
        from agents.followup.scheduler import generate_schedule
        schedule = generate_schedule("p1", "c1", "unknown_type")
        assert len(schedule) == 1  # falls back to routine

    def test_get_plan_for_diagnosis_chronic(self):
        from agents.followup.scheduler import get_plan_for_diagnosis
        assert get_plan_for_diagnosis("高血压") == "chronic_disease"
        assert get_plan_for_diagnosis("糖尿病") == "chronic_disease"
        assert get_plan_for_diagnosis("抑郁症") == "mental_health"
        assert get_plan_for_diagnosis("感冒") == "routine"

    def test_get_plan_for_diagnosis_mental(self):
        from agents.followup.scheduler import get_plan_for_diagnosis
        assert get_plan_for_diagnosis("焦虑症") == "mental_health"
        assert get_plan_for_diagnosis("失眠") == "mental_health"
