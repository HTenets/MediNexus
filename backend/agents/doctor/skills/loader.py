"""Skill loader — discovers and registers builtin skills.

Extends to external directory scanning in v0.3.0+ (community skills).
"""

import logging
from agents.doctor.skills.base import BaseSkill
from agents.doctor.skills.registry import registry

logger = logging.getLogger(__name__)


def load_builtin_skills():
    """Discover, instantiate(实例化), and register all builtin skills."""
    from agents.doctor.skills.builtin.internal_medicine.skill import InternalMedicineSkill
    from agents.doctor.skills.builtin.dermatology.skill import DermatologySkill
    from agents.doctor.skills.builtin.ent.skill import ENTSkill
    from agents.doctor.skills.builtin.mental_health.skill import MentalHealthSkill

    skill_classes = [
        InternalMedicineSkill, # 内医学技能
        DermatologySkill, # 皮肤科技能
        ENTSkill, # 鼻科技能
        MentalHealthSkill, # 心理健康技能
    ]

    for cls in skill_classes:
        try:
            instance = cls()
            registry.register(instance)
            logger.info("Registered skill: %s", instance.name)
        except Exception as e:
            logger.error("Failed to load skill %s: %s", cls.__name__, e)


def load_skills() -> dict[str, BaseSkill]:
    """Load all skills and return as name→instance dict (legacy compatibility)."""
    load_builtin_skills()
    return {name: registry.get(name) for name in registry.list_skills()}
