"""Skill system."""
from abc import ABC, abstractmethod


class BaseSkill(ABC):
    name: str
    system_prompt: str = ""

    @abstractmethod
    async def get_knowledge(self, context: dict) -> str:
        ...
