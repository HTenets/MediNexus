"""Anthropic (Claude) LLM client.

Uses ``httpx`` directly (no extra SDK dependency).
"""

import httpx

from llm.client import BaseLLMClient

ANTHROPIC_VERSION = "2023-06-01"


class AnthropicClient(BaseLLMClient):
    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        base_url: str = "https://api.anthropic.com",
        timeout: float = 90.0,
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def chat(self, messages: list[dict]) -> str:
        if not self.api_key:
            return ""

        system = ""
        turned = []
        for m in messages:
            if m["role"] == "system":
                system += m["content"] + "\n"
            else:
                turned.append({"role": m["role"], "content": m["content"]})

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": ANTHROPIC_VERSION,
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "max_tokens": 2048,
                    "system": system.strip(),
                    "messages": turned,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return "".join(
                block.get("text", "")
                for block in data.get("content", [])
                if block.get("type") == "text"
            )

    async def chat_stream(self, messages: list[dict]):
        text = await self.chat(messages)
        yield text
