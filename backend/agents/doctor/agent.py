from agents.base import BaseAgent
from app.schemas.agent import HandoverManifest


class DoctorAgent(BaseAgent):
    def __init__(self):
        super().__init__("doctor")

    async def run(self, context: dict) -> HandoverManifest:
        return HandoverManifest(
            facts=context.get("facts", []),
            pending_questions=["Differential diagnosis", "Treatment plan"],
            risk_flags=[],
            evidence_level="C",
        )
