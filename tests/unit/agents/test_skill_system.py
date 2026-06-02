"""Unit tests for the Skill system — BaseSkill, SkillRegistry, loader, and builtin skills."""

import pytest
from agents.doctor.skills.base import BaseSkill
from agents.doctor.skills.registry import SkillRegistry


class TestBaseSkill:
    """BaseSkill abstract interface."""

    def test_skill_requires_name(self):
        """Skill without name should not be registerable."""
        reg = SkillRegistry()
        skill = _TestSkill(name="", prompt="test")
        with pytest.raises(ValueError):
            reg.register(skill)

    @pytest.mark.asyncio
    async def test_skill_get_tools_default(self):
        skill = _TestSkill(name="test", prompt="prompt")
        tools = await skill.get_tools()
        assert tools == []

    @pytest.mark.asyncio
    async def test_skill_match_symptoms_default(self):
        """Base match_symptoms should return 0.0 (TestSkill returns 0.0 by default)."""
        skill = _TestSkill(name="test", prompt="prompt", match_score=0.0)
        score = await skill.match_symptoms("anything")
        assert score == 0.0


class TestSkillRegistry:
    """SkillRegistry registration and lookup."""

    def setup_method(self):
        self.reg = SkillRegistry()
        self.skill_a = _TestSkill(name="dept_a", prompt="prompt_a", match_score=0.9)
        self.skill_b = _TestSkill(name="dept_b", prompt="prompt_b", match_score=0.0)
        self.reg.register(self.skill_a)
        self.reg.register(self.skill_b)

    def test_register_and_get(self):
        skill = self.reg.get("dept_a")
        assert skill is not None
        assert skill.name == "dept_a"

    def test_get_nonexistent(self):
        skill = self.reg.get("nonexistent")
        assert skill is None

    def test_list_skills(self):
        names = self.reg.list_skills()
        assert "dept_a" in names
        assert "dept_b" in names
        assert len(names) == 2

    @pytest.mark.asyncio
    async def test_auto_route_exact_department(self):
        skill = await self.reg.auto_route("some symptoms", "dept_a")
        assert skill is not None
        assert skill.name == "dept_a"

    @pytest.mark.asyncio
    async def test_auto_route_symptom_match(self):
        skill = await self.reg.auto_route("fever and cough", "")
        assert skill is not None
        assert skill.name == "dept_a"  # dept_a has high match_score for "fever"

    @pytest.mark.asyncio
    async def test_auto_route_low_confidence_returns_first(self):
        reg = SkillRegistry()
        reg.register(_TestSkill(name="only_one", prompt="prompt", match_score=0.0))
        skill = await reg.auto_route("unknown symptoms", "")
        assert skill is not None
        assert skill.name == "only_one"

    @pytest.mark.asyncio
    async def test_auto_route_empty_registry(self):
        reg = SkillRegistry()
        skill = await reg.auto_route("anything", "")
        assert skill is None


class TestBuiltinSkills:
    """Builtin skills should load and have valid configurations."""

    def test_import_all_skills(self):
        """All 4 builtin skills should import without errors."""
        from agents.doctor.skills.builtin.internal_medicine.skill import InternalMedicineSkill
        from agents.doctor.skills.builtin.dermatology.skill import DermatologySkill
        from agents.doctor.skills.builtin.ent.skill import ENTSkill
        from agents.doctor.skills.builtin.mental_health.skill import MentalHealthSkill

        for cls in [InternalMedicineSkill, DermatologySkill, ENTSkill, MentalHealthSkill]:
            instance = cls()
            assert instance.name != ""
            assert instance.system_prompt != ""

    def test_builtin_skills_have_chinese_prompts(self):
        """Each skill's system_prompt should contain Chinese characters."""
        from agents.doctor.skills.builtin.internal_medicine.skill import InternalMedicineSkill
        from agents.doctor.skills.builtin.dermatology.skill import DermatologySkill
        from agents.doctor.skills.builtin.ent.skill import ENTSkill
        from agents.doctor.skills.builtin.mental_health.skill import MentalHealthSkill

        for cls in [InternalMedicineSkill, DermatologySkill, ENTSkill, MentalHealthSkill]:
            skill = cls()
            has_chinese = any('一' <= c <= '鿿' for c in skill.system_prompt)
            assert has_chinese, f"{skill.name} prompt lacks Chinese text"

    @pytest.mark.asyncio
    async def test_builtin_skills_return_knowledge(self):
        """get_knowledge() should return non-empty string for all skills."""
        from agents.doctor.skills.builtin.internal_medicine.skill import InternalMedicineSkill
        from agents.doctor.skills.builtin.dermatology.skill import DermatologySkill
        from agents.doctor.skills.builtin.ent.skill import ENTSkill
        from agents.doctor.skills.builtin.mental_health.skill import MentalHealthSkill

        for cls in [InternalMedicineSkill, DermatologySkill, ENTSkill, MentalHealthSkill]:
            skill = cls()
            knowledge = await skill.get_knowledge({"symptoms": "test symptom"})
            assert knowledge is not None
            assert len(knowledge) > 0, f"{skill.name} returned empty knowledge"

    @pytest.mark.asyncio
    async def test_builtin_skills_match_symptoms(self):
        """All skills should implement match_symptoms."""
        from agents.doctor.skills.builtin.internal_medicine.skill import InternalMedicineSkill
        from agents.doctor.skills.builtin.dermatology.skill import DermatologySkill
        from agents.doctor.skills.builtin.ent.skill import ENTSkill
        from agents.doctor.skills.builtin.mental_health.skill import MentalHealthSkill

        for cls in [InternalMedicineSkill, DermatologySkill, ENTSkill, MentalHealthSkill]:
            skill = cls()
            score = await skill.match_symptoms("test")
            # match_symptoms should return a float
            assert isinstance(score, float)

    @pytest.mark.asyncio
    async def test_internal_medicine_respiratory_knowledge(self):
        """Internal medicine should return respiratory knowledge for cough."""
        from agents.doctor.skills.builtin.internal_medicine.skill import InternalMedicineSkill
        skill = InternalMedicineSkill()
        knowledge = await skill.get_knowledge({"symptoms": "cough and fever for 3 days"})
        has_respiratory = "呼吸系统" in knowledge or "呼吸道" in knowledge or "感冒" in knowledge
        assert has_respiratory, f"Expected respiratory knowledge, got: {knowledge[:100]}"

    @pytest.mark.asyncio
    async def test_dermatology_rash_knowledge(self):
        """Dermatology should return rash-related knowledge."""
        from agents.doctor.skills.builtin.dermatology.skill import DermatologySkill
        skill = DermatologySkill()
        knowledge = await skill.get_knowledge({"symptoms": "red rash on arms, itchy"})
        has_derm = "荨麻疹" in knowledge or "湿疹" in knowledge or "瘙痒" in knowledge
        assert has_derm, f"Expected dermatology knowledge, got: {knowledge[:100]}"

    @pytest.mark.asyncio
    async def test_mental_health_match_suicide(self):
        """Mental health skill should detect suicide keywords."""
        from agents.doctor.skills.builtin.mental_health.skill import MentalHealthSkill
        skill = MentalHealthSkill()
        score = await skill.match_symptoms("suicidal thoughts and depression")
        assert score > 0.9, f"Expected high suicide match, got {score}"

    def test_phq9_calculation(self):
        """PHQ-9 calculator should return correct severity."""
        from agents.doctor.skills.builtin.mental_health.skill import MentalHealthSkill
        total, severity = MentalHealthSkill.calculate_phq9([2, 2, 1, 1, 0, 1, 1, 0, 0])
        assert total == 8
        assert severity == "轻度"

        # Severe case
        total2, severity2 = MentalHealthSkill.calculate_phq9([3, 3, 3, 2, 2, 2, 2, 1, 1])
        assert total2 == 19
        assert severity2 == "中重度"

    def test_gad7_calculation(self):
        """GAD-7 calculator should return correct severity."""
        from agents.doctor.skills.builtin.mental_health.skill import MentalHealthSkill
        total, severity = MentalHealthSkill.calculate_gad7([3, 3, 2, 2, 1, 1, 0])
        assert total == 12
        assert severity == "中度"


# ------------------------------------------------------------------ #
#  Test helper
# ------------------------------------------------------------------ #

class _TestSkill(BaseSkill):
    """Test skill with configurable attributes and match behavior."""

    def __init__(self, name: str = "test", prompt: str = "", match_score: float = 0.0):
        super().__init__()
        self._name = name
        self._prompt = prompt
        self._match_score = match_score

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def system_prompt(self):
        return self._prompt

    @system_prompt.setter
    def system_prompt(self, value):
        self._prompt = value

    async def get_knowledge(self, context: dict) -> str:
        return f"Knowledge for {self._name}"

    async def match_symptoms(self, symptoms: str) -> float:
        if "fever" in symptoms.lower() or "cough" in symptoms.lower():
            return 0.9
        return self._match_score
