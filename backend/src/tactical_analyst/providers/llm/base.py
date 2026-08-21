from typing import Protocol


class LLMProvider(Protocol):
    """Provider-neutral chat model factory."""

    def get_chat_model(self):
        """Return a provider chat model."""

