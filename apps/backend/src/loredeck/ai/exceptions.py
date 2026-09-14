class AIError(Exception):
    """Base error for provider-independent AI failures."""


class UnsupportedAIProviderError(AIError):
    """Raised when no implementation exists for a configured provider."""


class InvalidAIConfigurationError(AIError):
    """Raised when provider construction receives invalid configuration."""


class InvalidAIRequestError(AIError):
    """Raised when a provider-independent request cannot be serialized safely."""


class AIProviderUnavailableError(AIError):
    """Raised when the selected provider cannot serve a request."""


class AIProviderTimeoutError(AIError):
    """Raised when the selected provider exceeds its configured timeout."""


class AIProviderRefusalError(AIError):
    """Raised when the selected provider refuses a request."""


class InvalidAIProviderResponseError(AIError):
    """Raised when a provider result violates LoreDeck's contract."""
