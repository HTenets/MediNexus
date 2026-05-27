from agents.doctor.skills.base import BaseSkill


class ENTSkill(BaseSkill):
    name = "ent"
    system_prompt = "You are an ENT specialist."

    async def get_knowledge(self, context: dict) -> str:
        return "ENT knowledge: ear, nose, throat conditions."
