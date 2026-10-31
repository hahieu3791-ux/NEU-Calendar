from app.core.config import settings
from app.llm.base import BaseLLMProvider
from app.llm.mock_provider import MockLLMProvider
from app.llm.openai_provider import OpenAIProvider
from app.llm.gemini_provider import GeminiProvider
from app.llm.anthropic_provider import AnthropicProvider


def get_llm_provider() -> BaseLLMProvider:
    """Return configured LLM provider or Mock provider if no API keys are present."""
    provider_name = settings.LLM_PROVIDER.lower().strip()

    if provider_name == "openai" and settings.OPENAI_API_KEY:
        return OpenAIProvider(api_key=settings.OPENAI_API_KEY, model=settings.LLM_MODEL or "gpt-4o-mini")
    elif provider_name == "gemini" and settings.GEMINI_API_KEY:
        return GeminiProvider(api_key=settings.GEMINI_API_KEY, model=settings.LLM_MODEL or "gemini-1.5-flash")
    elif provider_name == "anthropic" and settings.ANTHROPIC_API_KEY:
        return AnthropicProvider(api_key=settings.ANTHROPIC_API_KEY, model=settings.LLM_MODEL or "claude-3-haiku-20240307")

    # Default to Mock provider
    return MockLLMProvider()
