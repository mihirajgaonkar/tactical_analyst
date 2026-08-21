from tactical_analyst.config.settings import Settings


def build_gemini_model(settings: Settings):
    """Build a Google Gemini LangChain chat model from settings."""

    if not settings.google_api_key:
        raise ValueError("GOOGLE_API_KEY is required for the Gemini provider")
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
    except ImportError as exc:
        raise RuntimeError("Install langchain-google-genai to use Gemini") from exc
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        temperature=settings.llm_temperature,
        max_retries=settings.llm_max_retries,
        timeout=settings.llm_timeout_seconds,
    )
