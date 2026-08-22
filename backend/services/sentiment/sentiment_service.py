from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.models.news import News
from backend.models.sentiment import Sentiment

from backend.repositories.sentiment_repository import (
    get_sentiment_by_news_id,
    upsert_sentiment,
)

from backend.services.sentiment.exceptions import (
    EmptyNewsContentError,
    InvalidSentimentResultError,
    NewsNotFoundError,
    SentimentProcessingError,
)

from backend.services.sentiment.preprocessor import (
    SentimentPreprocessor,
)

from backend.services.sentiment.provider import (
    SentimentProvider,
)

from backend.repositories.sentiment_repository import (
    get_company_sentiments,
)
from backend.services.sentiment.aggregator import (
    SentimentAggregator,
)
from backend.repositories.company_repository import (
    get_company_by_symbol,
)
from backend.repositories.news_repository import (
    list_latest_news,
    filter_unanalyzed_news,
)

from backend.services.sentiment.finbert_provider import (
    FinBERTProvider,
)


class SentimentService:
    """
    Business service responsible for article-level
    and batch sentiment analysis.
    """

    VALID_SENTIMENTS = {
        "positive",
        "negative",
        "neutral",
    }

    def __init__(
        self,
        provider: SentimentProvider,
        preprocessor: SentimentPreprocessor | None = None,
        aggregator: SentimentAggregator | None = None,
    ):
        self.provider = provider

        self.preprocessor = (
            preprocessor
            if preprocessor is not None
            else SentimentPreprocessor()
        )

        self.aggregator = (
            aggregator
            if aggregator is not None
            else SentimentAggregator()
        )
    # ---------------------------------------------------------
    # Read existing sentiment
    # ---------------------------------------------------------

    def get_article_sentiment(
        self,
        db: Session,
        news_id: int,
    ) -> Sentiment | None:
        """
        Return stored sentiment for a news article.
        """

        return get_sentiment_by_news_id(
            db,
            news_id,
        )

    # ---------------------------------------------------------
    # Single article analysis
    # ---------------------------------------------------------

    def analyze_article(
        self,
        db: Session,
        news_id: int,
        force: bool = False,
    ) -> Sentiment:
        """
        Analyze one news article and persist its sentiment.
        """

        try:

            news = self._get_news(
                db,
                news_id,
            )

            existing = get_sentiment_by_news_id(
                db,
                news_id,
            )

            if existing is not None and not force:
                return existing

            text = self._prepare_news_text(
                news,
            )

            prediction = self.provider.analyze(
                text,
            )

            self._validate_result(
                prediction,
            )

            return upsert_sentiment(
                db=db,
                news_id=news.id,
                model=prediction["model"],
                sentiment=prediction["sentiment"],
                confidence=prediction["confidence"],
            )

        except (
            NewsNotFoundError,
            EmptyNewsContentError,
            InvalidSentimentResultError,
        ):
            raise

        except SQLAlchemyError as exc:

            db.rollback()

            raise SentimentProcessingError(
                "Database error while processing "
                f"news article '{news_id}'."
            ) from exc

        except Exception as exc:

            raise SentimentProcessingError(
                "Failed to analyze "
                f"news article '{news_id}'."
            ) from exc

    # ---------------------------------------------------------
    # Batch analysis
    # ---------------------------------------------------------

    def analyze_news_batch(
        self,
        db: Session,
        news_ids: list[int],
        batch_size: int = 16,
        force: bool = False,
    ) -> list[Sentiment]:
        """
        Analyze multiple news articles using batched
        provider inference.
        """

        if not news_ids:
            return []

        if batch_size <= 0:
            raise ValueError(
                "batch_size must be greater than zero."
            )

        unique_news_ids = list(
            dict.fromkeys(news_ids)
        )

        news_records = (
            db.query(News)
            .filter(
                News.id.in_(unique_news_ids),
            )
            .all()
        )

        news_by_id = {
            news.id: news
            for news in news_records
        }

        missing_ids = [
            news_id
            for news_id in unique_news_ids
            if news_id not in news_by_id
        ]

        if missing_ids:
            raise NewsNotFoundError(
                "News articles not found: "
                f"{missing_ids}"
            )

        existing_records = {}

        if not force:

            existing = (
                db.query(Sentiment)
                .filter(
                    Sentiment.news_id.in_(
                        unique_news_ids,
                    ),
                )
                .all()
            )

            existing_records = {
                record.news_id: record
                for record in existing
            }

        articles_to_analyze = []

        for news_id in unique_news_ids:

            if (
                not force
                and news_id in existing_records
            ):
                continue

            articles_to_analyze.append(
                news_by_id[news_id]
            )

        if not articles_to_analyze:

            return [
                existing_records[news_id]
                for news_id in unique_news_ids
            ]

        results_by_news_id = {}

        for start in range(
            0,
            len(articles_to_analyze),
            batch_size,
        ):

            batch = articles_to_analyze[
                start:start + batch_size
            ]

            texts = []

            for news in batch:

                text = self._prepare_news_text(
                    news,
                )

                texts.append(text)

            try:

                predictions = (
                    self.provider.analyze_batch(
                        texts,
                    )
                )

            except Exception as exc:

                raise SentimentProcessingError(
                    "Sentiment provider failed while "
                    "processing a batch."
                ) from exc

            if len(predictions) != len(batch):

                raise InvalidSentimentResultError(
                    "Sentiment provider returned "
                    "an unexpected number of predictions."
                )

            for news, prediction in zip(
                batch,
                predictions,
            ):

                self._validate_result(
                    prediction,
                )

                sentiment_record = upsert_sentiment(
                    db=db,
                    news_id=news.id,
                    model=prediction["model"],
                    sentiment=prediction["sentiment"],
                    confidence=prediction["confidence"],
                )

                results_by_news_id[
                    news.id
                ] = sentiment_record

        return [
            results_by_news_id.get(
                news_id,
                existing_records.get(news_id),
            )
            for news_id in unique_news_ids
        ]

    # ---------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------

    @staticmethod
    def _get_news(
        db: Session,
        news_id: int,
    ) -> News:
        """
        Load a news article or raise a domain exception.
        """

        news = (
            db.query(News)
            .filter(
                News.id == news_id,
            )
            .first()
        )

        if news is None:

            raise NewsNotFoundError(
                f"News article '{news_id}' not found."
            )

        return news

    def _prepare_news_text(
        self,
        news: News,
    ) -> str:
        """
        Prepare a News entity for sentiment analysis.
        """

        try:

            return self.preprocessor.prepare(
                title=news.title,
                summary=news.summary,
                content=news.content,
            )

        except ValueError as exc:

            raise EmptyNewsContentError(
                f"News article '{news.id}' "
                "does not contain usable text."
            ) from exc

    def _validate_result(
        self,
        result: dict,
    ) -> None:
        """
        Validate the standardized provider response.
        """

        if not isinstance(result, dict):

            raise InvalidSentimentResultError(
                "Sentiment provider must return a dictionary."
            )

        required_fields = {
            "sentiment",
            "confidence",
            "model",
        }

        missing = (
            required_fields
            - result.keys()
        )

        if missing:

            raise InvalidSentimentResultError(
                "Sentiment provider returned "
                f"missing fields: {missing}"
            )

        sentiment = result["sentiment"]

        if sentiment not in self.VALID_SENTIMENTS:

            raise InvalidSentimentResultError(
                "Invalid sentiment returned by provider: "
                f"{sentiment}"
            )

        confidence = result["confidence"]

        if not isinstance(
            confidence,
            (float, int),
        ):

            raise InvalidSentimentResultError(
                "Sentiment confidence must be numeric."
            )

        confidence = float(confidence)

        if not 0.0 <= confidence <= 1.0:

            raise InvalidSentimentResultError(
                "Sentiment confidence must be "
                "between 0 and 1."
            )

        model = result["model"]

        if not isinstance(
            model,
            str,
        ) or not model.strip():

            raise InvalidSentimentResultError(
                "Sentiment model cannot be empty."
            )

    def get_company_sentiment(
        self,
        db: Session,
        company_id: int,
        limit: int = 100,
        provider: str | None = None,
    ) -> dict:
        """
        Calculate overall sentiment for a company
        using stored article-level sentiment results.
        """

        if limit <= 0:
            raise ValueError(
                "limit must be greater than zero."
            )

        records = get_company_sentiments(
            db=db,
            company_id=company_id,
            limit=limit,
            provider=provider,
        )

        sentiment_data = [
            {
                "sentiment": record.sentiment,
                "confidence": record.confidence,
            }
            for record in records
        ]

        return self.aggregator.aggregate(
            sentiment_data,
        )

    def get_company_sentiment_by_symbol(
        self,
        db: Session,
        symbol: str,
        limit: int = 100,
        provider: str | None = None,
    ) -> dict:

        symbol = symbol.strip().upper()

        if not symbol:
            raise ValueError(
                "Company symbol cannot be empty."
            )

        if provider is not None:
            provider = provider.strip().lower()

            if not provider:
                provider = None

        company = get_company_by_symbol(
            db,
            symbol,
        )

        if company is None:
            raise ValueError(
                f"Company '{symbol}' not found."
            )

        result = self.get_company_sentiment(
            db=db,
            company_id=company.id,
            limit=limit,
            provider=provider,
        )

        return {
            "symbol": company.symbol,
            **result,
        }
    
    def analyze_company_news(
        self,
        db: Session,
        company_id: int,
        limit: int = 100,
        batch_size: int = 16,
        provider: str | None = None,
    ) -> list[Sentiment]:
        """
        Analyze the latest company news.

        The process is:

        1. Select the latest `limit` news articles.
        2. Optionally filter by provider.
        3. Remove articles that already have sentiment.
        4. Run FinBERT in batches.
        """

        if limit <= 0:
            raise ValueError(
                "limit must be greater than zero."
            )

        if batch_size <= 0:
            raise ValueError(
                "batch_size must be greater than zero."
            )

        if provider is not None:
            provider = provider.strip().lower()

            if not provider:
                provider = None

        # ---------------------------------------------------------
        # Step 1: Select latest news
        # ---------------------------------------------------------

        news_records = list_latest_news(
            db=db,
            company_id=company_id,
            limit=limit,
            provider=provider,
        )

        if not news_records:
            return []

        # ---------------------------------------------------------
        # Step 2: Remove already analyzed articles
        # ---------------------------------------------------------

        news_records = filter_unanalyzed_news(
            db=db,
            news_records=news_records,
        )

        if not news_records:
            return []

        # ---------------------------------------------------------
        # Step 3: Extract IDs
        # ---------------------------------------------------------

        news_ids = [
            news.id
            for news in news_records
        ]

        # ---------------------------------------------------------
        # Step 4: Batch sentiment analysis
        # ---------------------------------------------------------

        return self.analyze_news_batch(
            db=db,
            news_ids=news_ids,
            batch_size=batch_size,
            force=False,
        )

sentiment_provider = FinBERTProvider()

sentiment_preprocessor = SentimentPreprocessor()

sentiment_service = SentimentService(
    provider=sentiment_provider,
    preprocessor=sentiment_preprocessor,
)