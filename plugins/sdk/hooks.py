"""Plugin lifecycle hooks."""

from typing import Any


class PluginHooks:
    async def on_agent_pre_process(self, context: dict[str, Any]) -> dict[str, Any]:
        return context

    async def on_agent_post_process(self, result: Any) -> Any:
        return result
