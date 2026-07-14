"""Ollama LLM client (local models).

Uses ``httpx`` to call the Ollama ``/api/chat`` endpoint. Falls back to
empty string when unavailable so callers can degrade gracefully.
"""

import httpx

from llm.client import BaseLLMClient


class OllamaClient(BaseLLMClient):
    def __init__(
        self,
        model: str = "qwen2.5:14b",
        base_url: str = "http://localhost:11434",
        timeout: float = 120.0,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def chat(self, messages: list[dict]) -> str:
        payload_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in messages
            if m["role"] in ("system", "user", "assistant")
        ]
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": payload_messages,
                        "stream": False,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                return data.get("message", {}).get("content", "")
            except (httpx.HTTPError, KeyError, ValueError):
                return ""

    async def chat_stream(self, messages: list[dict]):
        text = await self.chat(messages)
        yield text
