"""LLM client factory — builds the right provider from application settings.

Provider selection (``MEDINEXUS_LLM_PROVIDER``):
  - ``openai`` / ``deepseek`` / ``moonshot`` -> OpenAI-compatible client
  - ``anthropic``                          -> Anthropic (Claude) client
  - ``ollama``                            -> local Ollama client

Returns ``None`` when no provider can be built (callers then degrade to
rule-based mode).
"""

from app.config import settings
from llm.client import BaseLLMClient
from llm.providers.anthropic import AnthropicClient
from llm.providers.ollama import OllamaClient
from llm.providers.openai import OpenAIClient

_DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "deepseek": "deepseek-chat",
    "moonshot": "moonshot-v1-8k",
    "anthropic": "claude-3-5-sonnet-20241022",
    "ollama": "qwen2.5:14b",
}

_DEFAULT_BASE_URLS = {
    "openai": "https://api.openai.com/v1",
    "deepseek": "https://api.deepseek.com/v1",
    "moonshot": "https://api.moonshot.cn/v1",
}


def create_llm_client() -> BaseLLMClient | None:
    """Build an LLM client from the current settings, or ``None``."""
    provider = (settings.llm_provider or "ollama").lower()

    if provider == "anthropic":
        if not settings.llm_api_key:
            return None
        return AnthropicClient(
            api_key=settings.llm_api_key,
            model=settings.llm_model or _DEFAULT_MODELS["anthropic"],
            base_url=settings.llm_base_url or "https://api.anthropic.com",
        )

    if provider == "ollama":
        return OllamaClient(
            model=settings.ollama_model or _DEFAULT_MODELS["ollama"],
            base_url=settings.ollama_base_url or "http://localhost:11434",
        )

    # openai / deepseek / moonshot -> OpenAI-compatible
    if not settings.llm_api_key:
        return None
    return OpenAIClient(
        api_key=settings.llm_api_key,
        model=settings.llm_model or _DEFAULT_MODELS.get(provider, "gpt-4o-mini"),
        base_url=settings.llm_base_url or _DEFAULT_BASE_URLS.get(provider, "https://api.openai.com/v1"),
    )
