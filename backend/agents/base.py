"""BaseAgent — abstract base for all agents with hook and tool-calling interfaces."""

import inspect
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable
from app.schemas.agent import HandoverManifest

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """All agents inherit from this class.

    Each agent implements run() to process context and produce a HandoverManifest.
    Hooks (on_pre_process, on_post_process) apply guardrails (PII sanitization,
    emergency detection) before and after agent execution.
    """

    def __init__(self, name: str):
        self.name = name
        self.tools: dict[str, Callable] = {}

    @abstractmethod
    async def run(self, context: dict[str, Any]) -> HandoverManifest:
        """Process the given context and return a HandoverManifest."""

    async def on_pre_process(self, context: dict[str, Any]) -> dict[str, Any]:
        """Pre-process hook — sanitizes PII and detects emergencies before run().

        - PII in symptoms/patient_history is masked before being sent to LLMs.
        - Emergency signals are detected and flagged in the context.
        """
        from guardrails.pii_sanitizer import PIISanitizer
        from guardrails.emergency_detector import EmergencyDetector

        sanitizer = PIISanitizer()
        detector = EmergencyDetector()

        # Sanitize PII in user-facing text fields before LLM exposure
        for field in ("symptoms", "patient_history"):
            raw = context.get(field, "")
            if isinstance(raw, str) and raw:
                context[field] = sanitizer.sanitize_text(raw)

        # Detect emergency signals
        symptoms = context.get("symptoms", "")
        if isinstance(symptoms, str) and symptoms:
            is_emergency, detected_kws, etype = await detector.check(symptoms)
            if is_emergency:
                context["_emergency_detected"] = True
                context["_emergency_type"] = etype
                context["_emergency_keywords"] = detected_kws
                logger.warning(
                    "Emergency detected by guardrail in agent '%s': type=%s, keywords=%s",
                    self.name, etype, detected_kws,
                )

        return context

    async def on_post_process(self, result: HandoverManifest) -> HandoverManifest:
        """Post-process hook — ensures emergency risk flags are propagated."""
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
