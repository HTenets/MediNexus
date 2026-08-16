"""Session state & graph state definitions."""

from typing import Any, TypedDict, Optional
from dataclasses import dataclass, field


@dataclass
class SessionState:
    """API-level session state — used for endpoint and session management."""
    session_id: str
    patient_id: str
    owner_id: str | None = None
    current_agent: str = "triage"
    history: list[dict] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)


class GraphState(TypedDict):
    """LangGraph internal state — a TypedDict for StateGraph compatibility."""
    session_id: str
    patient_id: str
    current_agent: str
    messages: list[dict]             # conversation messages
    context: dict[str, Any]          # shared context between agents
    pending_questions: list[str]     # questions still needing answers
    risk_flags: list[str]            # any risk flags raised
    evidence_level: str              # A / B / C
    agent_output: Optional[str]      # latest agent text output for streaming
    error: Optional[str]             # error message if any
