"""BaseAgent — abstract base for all agents with hook and tool-calling interfaces."""

import inspect
from abc import ABC, abstractmethod
from typing import Any, Callable
from app.schemas.agent import HandoverManifest


class BaseAgent(ABC):
    """All agents inherit from this class.

    Each agent implements run() to process context and produce a HandoverManifest.
    Hooks (on_pre_process, on_post_process) serve as Plugin injection points.
    """

    def __init__(self, name: str):
        self.name = name
        self.tools: dict[str, Callable] = {}

    @abstractmethod
    async def run(self, context: dict[str, Any]) -> HandoverManifest:
        """Process the given context and return a HandoverManifest."""

    async def on_pre_process(self, context: dict[str, Any]) -> dict[str, Any]:
        """Pre-process hook — called before run().
        Reserved for Plugin injection (identity verification, PII sanitization, etc.).
        """
        return context

    async def on_post_process(self, result: HandoverManifest) -> HandoverManifest:
        """Post-process hook — called after run().
        Reserved for Plugin injection (audit logging, result enrichment, etc.).
        """
        return result

    def register_tool(self, name: str, fn: Callable):
        """Register a tool that this agent can invoke during run()."""
        self.tools[name] = fn

    async def execute_tool(self, name: str, **kwargs: Any) -> Any:
        """Execute a registered tool by name."""
        fn = self.tools.get(name)
        if not fn:
            raise ValueError(f"Tool '{name}' not registered on agent '{self.name}'")
        return await fn(**kwargs) if inspect.iscoroutinefunction(fn) else fn(**kwargs)
