"""SkillRegistry — central registry for medical specialty skills.

Provides registration, lookup by name, and symptom-based auto-routing.
"""

from typing import Any
from agents.doctor.skills.base import BaseSkill


class SkillRegistry:
    """Registry mapping skill names to BaseSkill instances."""

    def __init__(self):
        self._skills: dict[str, BaseSkill] = {}

    def register(self, skill: BaseSkill):
        """Register a skill instance by its name."""
        if not skill.name:
            raise ValueError(f"Skill must have a non-empty name: {type(skill).__name__}")
        self._skills[skill.name] = skill

    def get(self, name: str) -> BaseSkill | None:
        """Lookup a skill by name (e.g. 'internal_medicine')."""
        return self._skills.get(name)

    def list_skills(self) -> list[str]:
        """Return all registered skill names."""
        return list(self._skills.keys())

    async def auto_route(self, symptoms: str, department: str = "") -> BaseSkill | None:
        """Select the best matching skill.

        Priority:
          1. 精确科室匹配 (from TriageAgent)
          2. 症状匹配信度评分 (match_symptoms)
          3. 回退到第一个注册的技能或None(回退)
        """
        # 1. Exact department match
        if department and department in self._skills:
            return self._skills[department]

        # 2. Symptom-based confidence scoring
        if symptoms:
            best_score = 0.0
            best_skill = None
            for skill in self._skills.values():
                score = await skill.match_symptoms(symptoms)
                if score > best_score:
                    best_score = score
                    best_skill = skill
            if best_score > 0.3:  # confidence threshold
                return best_skill

        # 3. Fallback
        if self._skills:
            return next(iter(self._skills.values()))
        return None


# Module-level singleton
registry = SkillRegistry()
