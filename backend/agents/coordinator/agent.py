from agents.base import BaseAgent
from agents.registry import registry
from app.schemas.agent import HandoverManifest
from typing import Any

# Complexity triggers for multi-specialty consultations
# Each trigger defines keywords, required specialties, and reason
COMPLEXITY_TRIGGERS: dict[str, dict[str, Any]] = {
    "skin_systemic": {
        "keywords": ["fever", "rash", "joint pain", "全身皮疹", "发热"],
        "specialties": ["dermatology", "internal_medicine"],
        "reason": "Skin manifestation with systemic symptoms requires cross-specialty evaluation",
    },
    "mental_physical": {
        "keywords": ["chest pain", "anxiety", "palpitation", "胸闷", "心悸", "焦虑"],
        "specialties": ["mental_health", "internal_medicine"],
        "reason": "Physical symptoms with mental health component requires coordinated care",
    },
    "neuro_cardiac": {
        "keywords": ["headache", "dizziness", "chest tightness", "头痛", "头晕", "胸痛"],
        "specialties": ["neurology", "internal_medicine"],
        "reason": "Neurological and cardiac symptoms overlap",
    },
    "multi_system": {
        "keywords": ["weight loss", "fatigue", "multi", "multiple", "消瘦", "乏力"],
        "specialties": ["internal_medicine", "endocrinology"],
        "reason": "Multi-system involvement suggests systemic disease",
    },
}


@registry.register
class CoordinatorAgent(BaseAgent):
    """Manages multi-specialty consultations."""

    def __init__(self):
        super().__init__("coordinator")
        self.participants: list[str] = []  # 参与者

    async def run(self, context: dict) -> HandoverManifest:
        specialties = context.get("required_specialties", [])
        symptoms = (context.get("symptoms", "") or "").lower()
        urgency = context.get("urgency", "")
        department = context.get("department", "")

        # Check complexity triggers against symptoms
        triggered_specialties: set[str] = set()
        consultation_needed = False
        trigger_reasons: list[str] = []

        for name, trigger in COMPLEXITY_TRIGGERS.items():
            for kw in trigger["keywords"]:
                if kw.lower() in symptoms:
                    triggered_specialties.update(trigger["specialties"])
                    consultation_needed = True
                    trigger_reasons.append(trigger["reason"])
                    break

        # If department is specified, include it
        if department:
            triggered_specialties.add(department)

        # Merge with explicitly required specialties
        triggered_specialties.update(specialties)
        self.participants = list(triggered_specialties)

        risk_flags: list[str] = []
        if urgency == "emergency" or any(kw in symptoms for kw in ["severe chest pain", "difficulty breathing"]):
            risk_flags.append("EMERGENCY_DETECTED")

        if consultation_needed:
            facts = [
                f"Multi-specialty consultation needed: {', '.join(triggered_specialties)}",
                f"Reasons: {'; '.join(trigger_reasons)}",
            ]
        else:
            facts = [f"Consultation not needed for symptoms: {symptoms}"]

        return HandoverManifest(
            facts=facts,
            pending_questions=["Collect specialty opinions", "Synthesize consensus"],
            risk_flags=risk_flags,
            context={
                "consultation_needed": consultation_needed,
                "specialties_consulted": list(triggered_specialties),
                "trigger_reasons": trigger_reasons,
            },
        )

    async def invite_specialist(self, specialty: str) -> Any:
        # Stub: triggers DoctorAgent with matching skill
        from agents.doctor.skills.registry import registry as skill_registry
        from agents.doctor.skills.loader import load_skills

        skills = load_skills()
        skill_available = specialty in skills
        return {
            "specialty": specialty,
            "status": "invited" if skill_available else "not_found",
            "skill_available": skill_available,
        }
