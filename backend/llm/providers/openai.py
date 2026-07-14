"""OpenAI-compatible LLM client.

Works with OpenAI, DeepSeek, Moonshot, and any OpenAI-compatible endpoint
by setting ``base_url``. Uses ``httpx`` (no extra SDK dependency).

Includes retry logic for transient failures and true streaming support.
"""

import logging

import httpx

from llm.client import BaseLLMClient

logger = logging.getLogger(__name__)

_MAX_RETRIES = 3
_RETRY_DELAYS = [1.0, 2.0, 4.0]  # seconds


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

        import asyncio

        last_error: Exception | None = None
        for attempt in range(_MAX_RETRIES):
            try:
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
            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                last_error = e
                if attempt < _MAX_RETRIES - 1:
                    delay = _RETRY_DELAYS[attempt]
                    logger.warning(
                        "OpenAI request failed (attempt %d/%d), retrying in %.1fs: %s",
                        attempt + 1, _MAX_RETRIES, delay, e,
                    )
                    await asyncio.sleep(delay)

        logger.error("OpenAI request failed after %d retries: %s", _MAX_RETRIES, last_error)
        return ""

    async def chat_stream(self, messages: list[dict]):
        """True streaming using SSE from the OpenAI-compatible API."""
        if not self.api_key:
            return

        import asyncio

        last_error: Exception | None = None
        for attempt in range(_MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    async with client.stream(
                        "POST",
                        f"{self.base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": self.model,
                            "messages": messages,
                            "temperature": 0.3,
                            "stream": True,
                        },
                    ) as resp:
                        resp.raise_for_status()
                        async for line in resp.aiter_lines():
                            if not line.startswith("data: "):
                                continue
                            payload = line[6:]
                            if payload.strip() == "[DONE]":
                                break
                            try:
                                import json
                                chunk = json.loads(payload)
                                delta = chunk["choices"][0].get("delta", {}).get("content", "")
                                if delta:
                                    yield delta
                            except (json.JSONDecodeError, KeyError, IndexError):
                                continue
                        return  # Success — exit retry loop
            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                last_error = e
                if attempt < _MAX_RETRIES - 1:
                    delay = _RETRY_DELAYS[attempt]
                    logger.warning(
                        "OpenAI stream failed (attempt %d/%d), retrying: %s",
                        attempt + 1, _MAX_RETRIES, e,
                    )
                    await asyncio.sleep(delay)

        logger.error("OpenAI stream failed after %d retries: %s", _MAX_RETRIES, last_error)
