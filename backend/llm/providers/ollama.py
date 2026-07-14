"""Ollama LLM client (local models).

Uses ``httpx`` to call the Ollama ``/api/chat`` endpoint. Falls back to
empty string when unavailable so callers can degrade gracefully.

Includes true streaming support via Ollama's native streaming mode.
"""

import logging

import httpx

from llm.client import BaseLLMClient

logger = logging.getLogger(__name__)


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
            except (httpx.HTTPError, KeyError, ValueError) as e:
                logger.warning("Ollama chat failed: %s", e)
                return ""

    async def chat_stream(self, messages: list[dict]):
        """True streaming using Ollama's newline-delimited JSON streaming."""
        import json

        payload_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in messages
            if m["role"] in ("system", "user", "assistant")
        ]
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": payload_messages,
                        "stream": True,
                    },
                ) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        if not line.strip():
                            continue
                        try:
                            chunk = json.loads(line)
                            content = chunk.get("message", {}).get("content", "")
                            if content:
                                yield content
                            if chunk.get("done"):
                                break
                        except (json.JSONDecodeError, KeyError):
                            continue
        except (httpx.HTTPError, KeyError, ValueError) as e:
            logger.warning("Ollama stream failed: %s", e)
