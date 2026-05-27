from agents.doctor.skills.base import BaseSkill


class DermatologySkill(BaseSkill):
    name = "dermatology"
    system_prompt = "You are a dermatology specialist."

    async def get_knowledge(self, context: dict) -> str:
        return "Dermatology knowledge: skin conditions, treatments, differential diagnosis."
