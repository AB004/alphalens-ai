from backend.services.sentiment.finbert_provider import (
    FinBERTProvider,
)

from backend.services.sentiment.preprocessor import (
    SentimentPreprocessor,
)

from backend.services.sentiment.sentiment_service import (
    SentimentService,
)


sentiment_provider = FinBERTProvider()

sentiment_preprocessor = SentimentPreprocessor()

sentiment_service = SentimentService(
    provider=sentiment_provider,
    preprocessor=sentiment_preprocessor,
)