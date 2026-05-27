"""Supervisor Agent — routes patients to appropriate agents."""


class SupervisorAgent:
    """Routes and manages agent execution flow."""

    async def route(self, context: dict) -> str:
        # Returns agent name based on triage result
        return context.get("route", "triage")
