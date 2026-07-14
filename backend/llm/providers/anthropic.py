"""Anthropic (Claude) LLM client.

Uses ``httpx`` directly (no extra SDK dependency).
Includes retry logic for transient failures.
"""

import asyncio
import logging

import httpx

from llm.client import BaseLLMClient

logger = logging.getLogger(__name__)

ANTHROPIC_VERSION = "2023-06-01"
_MAX_RETRIES = 3
_RETRY_DELAYS = [1.0, 2.0, 4.0]


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

        last_error: Exception | None = None
        for attempt in range(_MAX_RETRIES):
            try:
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
            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                last_error = e
                if attempt < _MAX_RETRIES - 1:
                    delay = _RETRY_DELAYS[attempt]
                    logger.warning(
                        "Anthropic request failed (attempt %d/%d), retrying in %.1fs: %s",
                        attempt + 1, _MAX_RETRIES, delay, e,
                    )
                    await asyncio.sleep(delay)

        logger.error("Anthropic request failed after %d retries: %s", _MAX_RETRIES, last_error)
        return ""

    async def chat_stream(self, messages: list[dict]):
        """True streaming using SSE from the Anthropic API."""
        if not self.api_key:
            return

        system = ""
        turned = []
        for m in messages:
            if m["role"] == "system":
                system += m["content"] + "\n"
            else:
                turned.append({"role": m["role"], "content": m["content"]})

        last_error: Exception | None = None
        for attempt in range(_MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    async with client.stream(
                        "POST",
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
                            "stream": True,
                        },
                    ) as resp:
                        resp.raise_for_status()
                        import json
                        async for line in resp.aiter_lines():
                            if not line.startswith("data: "):
                                continue
                            try:
                                event = json.loads(line[6:])
                                if event.get("type") == "content_block_delta":
                                    delta = event.get("delta", {})
                                    if delta.get("type") == "text_delta":
                                        text = delta.get("text", "")
                                        if text:
                                            yield text
                            except (json.JSONDecodeError, KeyError):
                                continue
                        return
            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                last_error = e
                if attempt < _MAX_RETRIES - 1:
                    delay = _RETRY_DELAYS[attempt]
                    logger.warning(
                        "Anthropic stream failed (attempt %d/%d), retrying: %s",
                        attempt + 1, _MAX_RETRIES, e,
                    )
                    await asyncio.sleep(delay)

        logger.error("Anthropic stream failed after %d retries: %s", _MAX_RETRIES, last_error)
