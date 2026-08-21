from pathlib import Path

from tactical_analyst.config.settings import Settings


def test_settings_defaults() -> None:
    settings = Settings()

    assert settings.llm_provider == "gemini"
    assert settings.soccer_data_provider == "statsbomb_open"
    assert settings.object_storage_path == Path("./data/object_store")
