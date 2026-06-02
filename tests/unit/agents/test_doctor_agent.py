"""Unit tests for DoctorAgent — rule-based fallback, skill integration, downgrade mode."""

import pytest
from agents.doctor.agent import DoctorAgent
from agents.doctor.skills.registry import SkillRegistry
from agents.doctor.skills.loader import load_builtin_skills


class TestDoctorAgentRuleMode:
    """DoctorAgent in rule-based fallback mode (no LLM)."""

    def setup_method(self):
        self.agent = DoctorAgent()
        load_builtin_skills()

    @pytest.mark.asyncio
    async def test_rule_mode_returns_facts(self):
        """Rule mode should return facts for valid input."""
        manifest = await self.agent.run({"symptoms": "I have a headache for 2 days"})
        assert len(manifest.facts) > 0
        assert manifest.evidence_level == "C"

    @pytest.mark.asyncio
    async def test_rule_mode_downgrade_marker(self):
        """Rule mode should mark downgrade in first fact."""
        manifest = await self.agent.run({"symptoms": "cough and fever"})
        assert "[模式: 规则引擎]" in manifest.facts[0]

    @pytest.mark.asyncio
    async def test_rule_mode_has_pending_questions(self):
        """Rule mode should always ask follow-up questions."""
        manifest = await self.agent.run({"symptoms": "cough"})
        assert len(manifest.pending_questions) > 0

    @pytest.mark.asyncio
    async def test_rule_mode_empty_symptoms(self):
        """Empty symptoms should prompt for description."""
        manifest = await self.agent.run({"symptoms": ""})
        assert len(manifest.facts) > 0

    @pytest.mark.asyncio
    async def test_rule_mode_internal_medicine(self):
        """Internal medicine symptoms should get relevant advice."""
        manifest = await self.agent.run({
            "symptoms": "cough and fever for 3 days",
            "department": "internal_medicine",
        })
        facts_text = " ".join(manifest.facts)
        assert "上呼吸道" in facts_text or "感冒" in facts_text or "感染" in facts_text

    @pytest.mark.asyncio
    async def test_rule_mode_dermatology(self):
        """Dermatology symptoms should get relevant advice."""
        manifest = await self.agent.run({
            "symptoms": "red rash on arms, very itchy",
            "department": "dermatology",
        })
        facts_text = " ".join(manifest.facts)
        assert "湿疹" in facts_text or "荨麻疹" in facts_text or "瘙痒" in facts_text or "皮疹" in facts_text

    @pytest.mark.asyncio
    async def test_rule_mode_ent(self):
        """ENT symptoms should get relevant advice."""
        manifest = await self.agent.run({
            "symptoms": "sore throat and ear pain",
            "department": "ent",
        })
        facts_text = " ".join(manifest.facts)
        assert "咽炎" in facts_text or "中耳" in facts_text or "咽喉" in facts_text

    @pytest.mark.asyncio
    async def test_rule_mode_mental_health(self):
        """Mental health triage should get relevant advice."""
        manifest = await self.agent.run({
            "symptoms": "feeling very anxious and can't sleep",
            "department": "mental_health",
        })
        facts_text = " ".join(manifest.facts)
        assert "焦虑" in facts_text

    @pytest.mark.asyncio
    async def test_rule_mode_suicide_crisis(self):
        """Suicide keywords should trigger crisis response."""
        # Register the mental health skill for routing
        manifest = await self.agent.run({
            "symptoms": "I want to kill myself",
            "department": "mental_health",
        })
        facts_text = " ".join(manifest.facts)
        assert "危机" in facts_text or "热线" in facts_text

    @pytest.mark.asyncio
    async def test_rule_mode_emergency_flag(self):
        """Emergency urgency should trigger risk flags."""
        manifest = await self.agent.run({
            "symptoms": "chest pain",
            "urgency": "emergency",
        })
        assert "EMERGENCY_DETECTED" in manifest.risk_flags

    @pytest.mark.asyncio
    async def test_rule_mode_skill_auto_selection(self):
        """Department from triage should auto-select the right skill."""
        manifest = await self.agent.run({
            "symptoms": "itchy red spots",
            "department": "dermatology",
        })
        assert manifest.context.get("skill_used") == "dermatology"

    @pytest.mark.asyncio
    async def test_rule_mode_no_skill_fallback(self):
        """When no department matches, should not crash."""
        manifest = await self.agent.run({
            "symptoms": "unknown symptom xyz123",
            "department": "",
        })
        assert manifest is not None
        assert len(manifest.facts) > 0


class TestDoctorAgentLLMIntegration:
    """DoctorAgent with a mock LLM client."""

    class MockLLM:
        async def chat(self, messages: list[dict]) -> str:
            return """{
                "possible_diagnoses": [
                    {"diagnosis": "上呼吸道感染", "likelihood": "高", "reason": "发热咳嗽3天"}
                ],
                "treatment_plan": {
                    "lifestyle": ["多休息", "多饮水"],
                    "medications": [
                        {"name": "对乙酰氨基酚", "dosage": "500mg 必要时", "evidence_level": "C"}
                    ],
                    "when_to_see_doctor": "如高热超过3天请就医"
                },
                "red_flags": [],
                "pending_questions": ["有无咳痰?", "有无咽痛?"]
            }"""

    @pytest.mark.asyncio
    async def test_llm_mode_returns_structured_output(self):
        """LLM mode should parse JSON response into HandoverManifest."""
        agent = DoctorAgent()
        manifest = await agent.run({
            "symptoms": "cough and fever for 3 days",
            "department": "internal_medicine",
            "llm_client": self.MockLLM(),
        })
        assert len(manifest.facts) > 0
        # Should NOT have downgrade marker
        assert "[模式: 规则引擎]" not in manifest.facts[0]
        assert manifest.context.get("llm_mode") is True

    @pytest.mark.asyncio
    async def test_llm_mode_diagnosis_parsed(self):
        """Diagnosis should be structured in context."""
        agent = DoctorAgent()
        manifest = await agent.run({
            "symptoms": "cough",
            "llm_client": self.MockLLM(),
        })
        diagnosis = manifest.context.get("diagnosis", {})
        assert diagnosis != {}
        assert "possible_diagnoses" in diagnosis
        assert diagnosis["possible_diagnoses"][0]["diagnosis"] == "上呼吸道感染"


class TestDoctorAgentSkillIntegration:
    """DoctorAgent should correctly route to skills and use their knowledge."""

    def test_skill_loaded_after_first_call(self):
        """Skills should be lazy-loaded after first agent run."""
        agent = DoctorAgent()
        assert agent._skills_loaded is False

    @pytest.mark.asyncio
    async def test_skill_used_in_context(self):
        """Context should record which skill was used."""
        agent = DoctorAgent()
        manifest = await agent.run({
            "symptoms": "itchy skin",
            "department": "dermatology",
        })
        assert manifest.context.get("skill_used") == "dermatology"
