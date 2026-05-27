from llm.client import BaseLLMClient


class OllamaClient(BaseLLMClient):
    async def chat(self, messages: list[dict]) -> str:
        return ""

    async def chat_stream(self, messages: list[dict]):
        yield ""
