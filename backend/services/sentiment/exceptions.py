class SentimentError(Exception):
    """
    Base exception for sentiment-related errors.
    """


class NewsNotFoundError(SentimentError):
    """
    Raised when a requested news article does not exist.
    """


class InvalidSentimentResultError(SentimentError):
    """
    Raised when a sentiment provider returns an invalid result.
    """


class SentimentProcessingError(SentimentError):
    """
    Raised when sentiment processing fails.
    """


class EmptyNewsContentError(SentimentError):
    """
    Raised when a news article contains no usable text.
    """