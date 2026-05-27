"""BaseAgent — abstract base for all agents."""
from abc import ABC, abstractmethod
from typing import Any
from app.schemas.agent import HandoverManifest


class BaseAgent(ABC):
    """All agents inherit from this class."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def run(self, context: dict[str, Any]) -> HandoverManifest:
        ...

    async def on_pre_process(self, context: dict[str, Any]) -> dict[str, Any]:
        # Hook: Plugin injection point
        return context

    async def on_post_process(self, result: HandoverManifest) -> HandoverManifest:
        # Hook: Plugin injection point
        return result
