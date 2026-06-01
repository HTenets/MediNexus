"""AgentRegistry — central registry for all agent types."""

from typing import Any
from agents.base import BaseAgent
from app.schemas.agent import HandoverManifest


class AgentRegistry:
    """Global registry mapping agent names to their classes."""

    def __init__(self):
        self._agents: dict[str, type[BaseAgent]] = {}

    def register(self, agent_cls: type[BaseAgent]):
        """Register an agent class. Instantiate it to get the canonical name."""
        instance = agent_cls()
        self._agents[instance.name] = agent_cls
        return agent_cls

    def get(self, name: str) -> type[BaseAgent]:
        cls = self._agents.get(name)
        if not cls:
            raise KeyError(f"Agent '{name}' not registered. Available: {list(self._agents)}")
        return cls

    def create(self, name: str, **kwargs: Any) -> BaseAgent:
        """Create an agent instance by name, passing optional kwargs."""
        return self.get(name)(**kwargs)

    def list_agents(self) -> list[str]:
        return list(self._agents.keys())


# Module-level singleton
registry = AgentRegistry()
