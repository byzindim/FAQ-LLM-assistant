class FAQAssistantError(Exception):
    """Base exception for the app. All custom errors inherit from this."""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class LLMTimeoutError(FAQAssistantError):
    """Ollama did not respond in time."""
    pass


class LLMGenerationError(FAQAssistantError):
    """Ollama returned an error or invalid output."""
    pass


class OllamaUnavailableError(FAQAssistantError):
    """Ollama service is down."""
    pass
