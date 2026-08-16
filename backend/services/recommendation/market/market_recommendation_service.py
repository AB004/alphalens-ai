from sqlalchemy.orm import Session

from backend.models.company import Company

from backend.repositories.company_repository import (
    get_company_by_symbol,
)

from backend.repositories.financial_repository import (
    get_latest_financials,
)

from backend.repositories.sentiment_repository import (
    get_company_sentiments,
)

from backend.repositories.market_recommendation_repository import (
    create_market_recommendation,
    get_latest_market_recommendation,
    update_market_recommendation,
)

from backend.services.recommendation.market.financial_feature_extractor import (
    financial_feature_extractor,
)

from backend.services.recommendation.market.financial_scoring import (
    financial_scoring_engine,
)

from backend.services.recommendation.market.sentiment_scoring import (
    sentiment_scoring_engine,
)

from backend.services.recommendation.market.score_normalization import (
    score_normalizer,
)

from backend.services.recommendation.market.recommendation_aggregation import (
    recommendation_aggregation_engine,
)

from backend.services.recommendation.market.confidence_calculator import (
    confidence_calculator,
)

from backend.services.recommendation.market.explainable_reasoning import (
    explainable_reasoning_engine,
)

from backend.services.recommendation.market.market_recommendation_cache import (
    MARKET_RECOMMENDATION_CACHE_TTL_MINUTES,
    get_cache_age_seconds,
    get_recommendation_expiry,
    is_recommendation_fresh,
)


class MarketRecommendationService:
    """
    End-to-end Module 10 recommendation service.

    Pipeline:

        Financial Data
            ↓
        Financial Features
            ↓
        Financial Score

        News Sentiment
            ↓
        Sentiment Score

        Financial + Sentiment
            ↓
        Score Normalization
            ↓
        Recommendation Aggregation
            ↓
        Confidence
            ↓
        Explainable Reasoning
            ↓
        Persistence
    """

    # =========================================================
    # PUBLIC API
    # =========================================================

    def generate(
        self,
        db: Session,
        symbol: str,
        sentiment_limit: int = 100,
        provider: str | None = None,
        force: bool = False,
    ):
        symbol = symbol.strip().upper()

        # -----------------------------------------------------
        # COMPANY
        # -----------------------------------------------------

        company = get_company_by_symbol(
            db,
            symbol,
        )

        if company is None:
            raise ValueError(
                f"Company '{symbol}' not found."
            )

        # -----------------------------------------------------
        # CACHE CHECK
        # -----------------------------------------------------

        existing = get_latest_market_recommendation(
            db=db,
            company_id=company.id,
        )

        if (
            not force
            and is_recommendation_fresh(
                recommendation=existing,
                sentiment_limit=sentiment_limit,
                provider=provider,
                ttl_minutes=MARKET_RECOMMENDATION_CACHE_TTL_MINUTES,
            )
        ):
            return self._serialize(
                existing,
                company.symbol,
                provider,
                sentiment_limit,
                cached=True,
            )

        # -----------------------------------------------------
        # FINANCIAL SCORE
        # -----------------------------------------------------

        financial_result = (
            self._calculate_financial_score(
                db=db,
                company=company,
            )
        )

        # -----------------------------------------------------
        # SENTIMENT SCORE
        # -----------------------------------------------------

        sentiment_result = (
            self._calculate_sentiment_score(
                db=db,
                company=company,
                limit=sentiment_limit,
                provider=provider,
            )
        )

        # -----------------------------------------------------
        # NORMALIZATION
        # -----------------------------------------------------

        normalized_scores = (
            score_normalizer.normalize(
                financial_score=financial_result.score,
                sentiment_score=sentiment_result.score,
            )
        )

        # -----------------------------------------------------
        # RECOMMENDATION AGGREGATION
        # -----------------------------------------------------

        aggregation_result = (
            recommendation_aggregation_engine.aggregate(
                normalized_scores,
            )
        )

        # -----------------------------------------------------
        # CONFIDENCE
        # -----------------------------------------------------

        confidence_result = (
            confidence_calculator.calculate(
                aggregation_result,
            )
        )

        # -----------------------------------------------------
        # EXPLAINABLE REASONING
        # -----------------------------------------------------

        reasoning_result = (
            explainable_reasoning_engine.generate(
                recommendation=aggregation_result,
                confidence=confidence_result,
            )
        )

        # -----------------------------------------------------
        # SAVE / UPDATE
        # -----------------------------------------------------

        recommendation = (
            self._persist_recommendation(
                db=db,
                company=company,
                recommendation=aggregation_result,
                confidence=confidence_result,
                reasoning=reasoning_result,
                sentiment_limit=sentiment_limit,
                provider=provider,
            )
        )

        # -----------------------------------------------------
        # RESPONSE
        # -----------------------------------------------------

        return self._serialize(
            recommendation,
            company.symbol,
            provider,
            sentiment_limit,
            cached=False,
        )

    # =========================================================
    # FINANCIAL SCORE
    # =========================================================

    def _calculate_financial_score(
        self,
        db: Session,
        company: Company,
    ):
        """
        Calculate the financial component.

        Uses financial statements stored by Module 7.
        """

        statements = get_latest_financials(
            db=db,
            company_id=company.id,
        )

        if not statements:
            raise ValueError(
                f"No financial data found for "
                f"company '{company.symbol}'."
            )

        features = (
            financial_feature_extractor.extract(
                statements,
            )
        )

        return financial_scoring_engine.calculate(
            features,
        )

    # =========================================================
    # SENTIMENT SCORE
    # =========================================================

    def _calculate_sentiment_score(
        self,
        db: Session,
        company: Company,
        limit: int,
        provider: str | None,
    ):
        """
        Calculate sentiment using Module 9
        stored sentiment records.
        """

        sentiments = get_company_sentiments(
            db=db,
            company_id=company.id,
            limit=limit,
            provider=provider,
        )

        if not sentiments:
            if provider:
                raise ValueError(
                    "No sentiment data found for "
                    f"company '{company.symbol}' "
                    f"from provider '{provider}'."
                )

            raise ValueError(
                "No sentiment data found for "
                f"company '{company.symbol}'."
            )

        return sentiment_scoring_engine.calculate(
            sentiments,
        )

    # =========================================================
    # PERSISTENCE
    # =========================================================

    def _persist_recommendation(
        self,
        db: Session,
        company: Company,
        recommendation,
        confidence,
        reasoning,
        sentiment_limit: int,
        provider: str | None,
    ):
        """
        Create a new recommendation or update
        the latest recommendation.
        """

        existing = get_latest_market_recommendation(
            db=db,
            company_id=company.id,
        )

        if existing is None:

            return create_market_recommendation(
                db=db,
                company_id=company.id,
                recommendation=(
                    recommendation.recommendation
                ),
                score=recommendation.score,
                confidence=confidence.confidence,
                financial_score=(
                    recommendation.financial_score
                ),
                sentiment_score=(
                    recommendation.sentiment_score
                ),
                financial_reasoning=(
                    reasoning.financial_reasoning
                ),
                sentiment_reasoning=(
                    reasoning.sentiment_reasoning
                ),
                overall_reasoning=(
                    reasoning.overall_reasoning
                ),
                confidence_reasoning=(
                    reasoning.confidence_reasoning
                ),
                sentiment_limit=sentiment_limit,
                sentiment_provider=provider,
                model_version="v1",
            )

        return update_market_recommendation(
            db=db,
            recommendation=existing,
            recommendation_value=(
                recommendation.recommendation
            ),
            score=recommendation.score,
            confidence=confidence.confidence,
            financial_score=(
                recommendation.financial_score
            ),
            sentiment_score=(
                recommendation.sentiment_score
            ),
            financial_reasoning=(
                reasoning.financial_reasoning
            ),
            sentiment_reasoning=(
                reasoning.sentiment_reasoning
            ),
            overall_reasoning=(
                reasoning.overall_reasoning
            ),
            confidence_reasoning=(
                reasoning.confidence_reasoning
            ),
            sentiment_limit=sentiment_limit,
            sentiment_provider=provider,
            model_version="v1",
        )

    # =========================================================
    # SERIALIZATION
    # =========================================================

    def _serialize(
        self,
        recommendation,
        symbol: str,
        provider: str | None,
        sentiment_limit: int,
        cached: bool = False,
    ):
        return {
            "symbol": symbol,

            "recommendation": (
                recommendation.recommendation
            ),

            "score": recommendation.score,

            "confidence": recommendation.confidence,

            "financial_score": (
                recommendation.financial_score
            ),

            "sentiment_score": (
                recommendation.sentiment_score
            ),

            "financial_reasoning": (
                recommendation.financial_reasoning
            ),

            "sentiment_reasoning": (
                recommendation.sentiment_reasoning
            ),

            "overall_reasoning": (
                recommendation.overall_reasoning
            ),

            "confidence_reasoning": (
                recommendation.confidence_reasoning
            ),

            "model_version": (
                recommendation.model_version
            ),

            "sentiment_filter": {
                "limit": recommendation.sentiment_limit,
                "provider": recommendation.sentiment_provider,
            },

            "cache": {
                "cached": cached,

                "ttl_minutes": (
                    MARKET_RECOMMENDATION_CACHE_TTL_MINUTES
                ),

                "age_seconds": (
                    get_cache_age_seconds(
                        recommendation
                    )
                ),

                "expires_at": (
                    get_recommendation_expiry(
                        recommendation
                    )
                ),
            },

            "created_at": (
                recommendation.created_at
            ),

            "updated_at": (
                recommendation.updated_at
            ),
        }


market_recommendation_service = (
    MarketRecommendationService()
)