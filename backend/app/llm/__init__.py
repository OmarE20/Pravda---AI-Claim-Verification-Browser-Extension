from __future__ import annotations

from ..config import settings
from .base import LLMProvider


def get_llm_provider() -> LLMProvider:
    """Factory picking the configured provider. Defaults to OpenAI per the tech-stack spec."""
    if settings.llm_provider == "anthropic":
        from .anthropic_provider import AnthropicProvider

        if not settings.anthropic_api_key:
            raise RuntimeError("LLM_PROVIDER=anthropic but ANTHROPIC_API_KEY is not set")
        return AnthropicProvider(api_key=settings.anthropic_api_key, model=settings.anthropic_model)

    from .openai_provider import OpenAIProvider

    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    return OpenAIProvider(api_key=settings.openai_api_key, model=settings.openai_model)
