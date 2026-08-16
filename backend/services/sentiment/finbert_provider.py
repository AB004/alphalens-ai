from typing import Any

import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
)

from backend.services.sentiment.provider import (
    SentimentProvider,
)


class FinBERTProvider(SentimentProvider):
    """
    FinBERT implementation of the SentimentProvider.

    Uses ProsusAI/finbert for financial sentiment
    classification.

    The model is loaded lazily. This prevents the
    application from loading FinBERT during startup.
    """

    MODEL_NAME = "ProsusAI/finbert"

    LABELS = {
        0: "positive",
        1: "negative",
        2: "neutral",
    }

    def __init__(
        self,
        model_name: str = MODEL_NAME,
    ):
        self.model_name = model_name

        self.device = torch.device(
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        # Do not load the model during application startup.
        self.tokenizer = None
        self.model = None

    def _load_model(self) -> None:
        """
        Lazily load tokenizer and FinBERT model.

        The model is loaded only when sentiment
        analysis is actually requested.
        """

        if self.model is not None:
            return

        self.tokenizer = (
            AutoTokenizer.from_pretrained(
                self.model_name,
            )
        )

        self.model = (
            AutoModelForSequenceClassification
            .from_pretrained(
                self.model_name,
            )
        )

        self.model.to(self.device)

        self.model.eval()

    def _validate_text(
        self,
        text: str,
    ) -> str:
        """
        Validate and normalize input text.
        """

        if not isinstance(text, str):
            raise TypeError(
                "Sentiment input must be a string."
            )

        text = text.strip()

        if not text:
            raise ValueError(
                "Sentiment input cannot be empty."
            )

        return text

    def _predict(
        self,
        texts: list[str],
    ) -> list[dict[str, Any]]:
        """
        Run FinBERT inference for a batch of texts.
        """

        if not texts:
            return []

        texts = [
            self._validate_text(text)
            for text in texts
        ]

        # Load model only when inference is required.
        self._load_model()

        inputs = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt",
        )

        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
        }

        with torch.no_grad():

            outputs = self.model(
                **inputs,
            )

        probabilities = torch.softmax(
            outputs.logits,
            dim=-1,
        )

        results = []

        for probability in probabilities:

            confidence, class_index = torch.max(
                probability,
                dim=-1,
            )

            class_index = class_index.item()

            results.append(
                {
                    "sentiment": self.LABELS[
                        class_index
                    ],
                    "confidence": float(
                        confidence.item()
                    ),
                    "model": self.model_name,
                }
            )

        return results

    def analyze(
        self,
        text: str,
    ) -> dict[str, Any]:
        """
        Analyze a single financial text.
        """

        results = self._predict(
            [text],
        )

        return results[0]

    def analyze_batch(
        self,
        texts: list[str],
    ) -> list[dict[str, Any]]:
        """
        Analyze multiple financial texts.
        """

        return self._predict(
            texts,
        )