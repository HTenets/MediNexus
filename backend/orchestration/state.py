"""Session state definitions."""

from typing import Any
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
