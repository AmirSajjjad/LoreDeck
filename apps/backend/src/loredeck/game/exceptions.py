class DeckNotFoundError(Exception):
    """Raised when a requested deck does not exist."""


class InactiveDeckError(Exception):
    """Raised when a requested deck is not active."""


class InsufficientActiveCardsError(Exception):
    """Raised when a spread requires more active cards than are available."""
