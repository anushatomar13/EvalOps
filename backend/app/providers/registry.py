from app.core.config import settings
from app.providers.base import LLMProvider
from app.providers.mock import MockProvider, model_price_per_1k

# Which provider family a friendly model name belongs to.
OPENAI_MODELS = {"gpt-4.1", "gpt-4o", "gpt-4o-mini"}
ANTHROPIC_MODELS = {"claude", "claude-opus", "claude-haiku"}


def get_provider(model: str) -> LLMProvider:
    """Return a real provider when the matching API key is set, else the mock.

    This is what lets the whole platform run offline/free by default while
    transparently upgrading to real model calls once keys are configured.
    """
    if model in OPENAI_MODELS and settings.OPENAI_API_KEY:
        from app.providers.openai_provider import OpenAIProvider

        return OpenAIProvider(model, settings.OPENAI_API_KEY)

    if model in ANTHROPIC_MODELS and settings.ANTHROPIC_API_KEY:
        from app.providers.anthropic_provider import AnthropicProvider

        return AnthropicProvider(model, settings.ANTHROPIC_API_KEY)

    return MockProvider(model)


def price_per_1k_tokens(model: str) -> float:
    return model_price_per_1k(model)
