from agents.base import BaseAgent
from app.schemas.agent import HandoverManifest
from typing import Any


class CoordinatorAgent(BaseAgent):
    """Manages multi-specialty consultations."""

    def __init__(self):
        super().__init__("coordinator")
        self.participants: list[str] = []

    async def run(self, context: dict) -> HandoverManifest:
        specialties = context.get("required_specialties", [])
        self.participants = specialties
        return HandoverManifest(
            facts=[f"Consultation required: {', '.join(specialties)}"],
            pending_questions=["Collect specialty opinions", "Synthesize consensus"],
            risk_flags=[],
        )

    async def invite_specialist(self, specialty: str) -> Any:
        # Stub: triggers DoctorAgent with matching skill
        return {"specialty": specialty, "status": "invited"}
