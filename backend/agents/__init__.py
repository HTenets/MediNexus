from agents.base import BaseAgent
from agents.registry import AgentRegistry, registry
from agents.triage.agent import TriageAgent  # noqa: F401 — triggers @registry.register
from agents.doctor.agent import DoctorAgent  # noqa: F401 — triggers @registry.register
from agents.review.agent import ReviewAgent  # noqa: F401 — triggers @registry.register
from agents.coordinator.agent import CoordinatorAgent  # noqa: F401 — triggers @registry.register
from agents.followup.agent import FollowupAgent  # noqa: F401 — triggers @registry.register

__all__ = ["BaseAgent", "AgentRegistry", "registry"]
