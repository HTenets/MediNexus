"""BaseSkill — abstract base for all medical specialty skills.

All skills inherit from this class and provide:
  - name: unique skill identifier (matches TriageAgent department output)
  - system_prompt: specialty-specific system prompt (Chinese, Ollama-optimized)
  - get_knowledge(): contextual knowledge retrieval
  - get_tools(): optional tool definitions
  - match_symptoms(): optional auto-routing confidence score
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseSkill(ABC): # （Abstract Base Class，抽象基类）
    """Medical specialty skill. Each skill covers one department's knowledge."""

    name: str = ""
    system_prompt: str = ""

    @abstractmethod # （abstractmethod，抽象方法，所有子类必须实现  ）
    async def get_knowledge(self, context: dict[str, Any]) -> str:
        """Return specialty knowledge relevant to the given context (symptoms, history, etc.).

        This is called by DoctorAgent to inject relevant medical knowledge
        before generating the diagnosis prompt.
        """
        ...

    async def get_tools(self) -> list[dict]:
        """Return tool definitions available to this skill (optional).

        Each tool: {"name": str, "description": str, "parameters": {...}}
        """
        return []

    async def match_symptoms(self, symptoms: str) -> float:
        """Return a confidence score [0.0, 1.0] that this skill matches the symptoms.

        Used by SkillRegistry for auto-routing when no department is provided.
        Base implementation returns 0.0; override for intelligent matching.
        """
        return 0.0
