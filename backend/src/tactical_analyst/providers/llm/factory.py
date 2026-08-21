from tactical_analyst.config.settings import Settings
from tactical_analyst.providers.llm.gemini import build_gemini_model


def get_llm(settings: Settings):
    """Return the configured provider chat model."""

    if settings.llm_provider == "gemini":
        return build_gemini_model(settings)
    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
