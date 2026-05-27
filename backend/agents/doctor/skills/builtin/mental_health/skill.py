from agents.doctor.skills.base import BaseSkill


class MentalHealthSkill(BaseSkill):
    name = "mental_health"
    system_prompt = "You are a mental health specialist. Use PHQ-9, GAD-7 screening tools."

    async def get_knowledge(self, context: dict) -> str:
        return "Mental health knowledge: depression, anxiety, screening tools, crisis resources."

    async def screen_phq9(self, responses: list[int]) -> int:
        return sum(responses)

    async def screen_gad7(self, responses: list[int]) -> int:
        return sum(responses)
