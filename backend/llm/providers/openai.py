"""OpenAI-compatible LLM client.

Works with OpenAI, DeepSeek, Moonshot, and any OpenAI-compatible endpoint
by setting ``base_url``. Uses ``httpx`` (no extra SDK dependency).
"""

import httpx

from llm.client import BaseLLMClient


class OpenAIClient(BaseLLMClient):
    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = "https://api.openai.com/v1",
        timeout: float = 90.0,
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def chat(self, messages: list[dict]) -> str:
        if not self.api_key:
            return ""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.3,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def chat_stream(self, messages: list[dict]):
        text = await self.chat(messages)
        yield text
