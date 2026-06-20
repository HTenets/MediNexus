from agents.base import BaseAgent
from agents.registry import registry
from app.schemas.agent import HandoverManifest
from typing import Any


@registry.register
class CoordinatorAgent(BaseAgent):
    """Manages multi-specialty consultations."""

    def __init__(self):
        super().__init__("coordinator")
        self.participants: list[str] = [] # 参与者

    async def run(self, context: dict) -> HandoverManifest:
        specialties = context.get("required_specialties", [])
        self.participants = specialties
        return HandoverManifest(
            facts=[f"Consultation required: {', '.join(specialties)}"],
            pending_questions=["Collect specialty opinions", "Synthesize consensus"], # 收集专家意见，归纳共识
            risk_flags=[],
        )

    async def invite_specialist(self, specialty: str) -> Any:
        # Stub: triggers DoctorAgent with matching skill
        return {"specialty": specialty, "status": "invited"}
