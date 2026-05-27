from agents.doctor.skills.base import BaseSkill


class InternalMedicineSkill(BaseSkill):
    name = "internal_medicine"
    system_prompt = "You are an internal medicine specialist."

    async def get_knowledge(self, context: dict) -> str:
        return "Internal medicine knowledge: common conditions, diagnosis guidelines."
