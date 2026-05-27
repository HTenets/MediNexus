"""Session state definition."""
from typing import Any
from dataclasses import dataclass, field


@dataclass
class SessionState:
    session_id: str
    patient_id: str
    current_agent: str = "triage"
    history: list[dict] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
