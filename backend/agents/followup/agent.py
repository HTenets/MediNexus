from agents.base import BaseAgent
from app.schemas.agent import HandoverManifest
from datetime import datetime, timedelta


class FollowupAgent(BaseAgent):
    """Manages post-visit follow-up scheduling and monitoring."""

    def __init__(self):
        super().__init__("followup")

    async def run(self, context: dict) -> HandoverManifest:
        return HandoverManifest(
            facts=[f"Follow-up scheduled for patient"],
            pending_questions=["Medication adherence", "Symptom progression"],
            risk_flags=[],
        )

    async def schedule(self, patient_id: str, days_offset: int) -> dict:
        followup_date = datetime.utcnow() + timedelta(days=days_offset)
        return {"patient_id": patient_id, "scheduled_date": followup_date.isoformat()}
