"""Unified LLM client interface."""

from abc import ABC, abstractmethod


class BaseLLMClient(ABC):
    @abstractmethod
    async def chat(self, messages: list[dict]) -> str:
        ...

    @abstractmethod
    async def chat_stream(self, messages: list[dict]):
        ...
