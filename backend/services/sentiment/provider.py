from abc import ABC, abstractmethod
from typing import Any


class SentimentProvider(ABC):
    """
    Abstract interface for sentiment analysis providers.

    Implementations can use:
    - FinBERT
    - another local ML model
    - an external sentiment API
    """

    @abstractmethod
    def analyze(
        self,
        text: str,
    ) -> dict[str, Any]:
        """
        Analyze a single piece of text.

        Returns:
            {
                "sentiment": "positive",
                "confidence": 0.95,
                "model": "FinBERT"
            }
        """

        raise NotImplementedError

    @abstractmethod
    def analyze_batch(
        self,
        texts: list[str],
    ) -> list[dict[str, Any]]:
        """
        Analyze multiple texts.

        The returned list must preserve
        the same order as the input texts.
        """

        raise NotImplementedError