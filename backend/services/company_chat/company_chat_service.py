from sqlalchemy.orm import Session

from backend.services.company_chat.company_resolver import (
    company_resolver,
)

from backend.services.company_chat.question_classifier import (
    question_classifier,
)

from backend.services.company_chat.context_builder import (
    company_context_builder,
)

from backend.services.company_chat.company_conversation_service import (
    company_conversation_service,
)

from backend.services.chat.memory_service import (
    memory_service,
)

from backend.services.chat.conversation_service import (
    conversation_service,
)

from backend.services.company_chat.exceptions import (
    CompanyChatProcessingError,
    EmptyQuestionError,
)

from backend.services.company_chat.financial_context_retriever import (
    financial_context_retriever,
)

from backend.services.company_chat.question_classifier import (
    CompanyQuestionType,
)

from backend.services.company_chat.news_context_retriever import (
    news_context_retriever,
)

from backend.services.company_chat.hybrid_context_builder import (
    hybrid_context_builder,
)

from backend.services.company_chat.sentiment_context_retriever import (
    sentiment_context_retriever,
)

from backend.services.company_chat.recommendation_context_retriever import (
    recommendation_context_retriever,
)

from backend.services.company_chat.response_generator import (
    company_chat_response_generator,
)

from backend.services.company_chat.source_builder import (
    company_chat_source_builder,
)

from backend.services.company_chat.followup_resolver import (
    followup_resolver,
)

from backend.services.company_chat.conversation_validator import (
    company_conversation_validator,
)

class CompanyChatService:
    """
    Main orchestration service for Company Chat.

    Phase 3 responsibilities:

    1. Validate question
    2. Resolve company
    3. Create/validate company conversation
    4. Load conversation memory
    5. Classify question
    6. Build company context
    7. Persist messages
    """

    def process_question(
        self,
        db: Session,
        symbol: str,
        question: str,
        conversation_id: int | None = None,
    ):

        question = question.strip()

        if not question:
            raise EmptyQuestionError(
                "Company chat question cannot be empty."
            )

        # --------------------------------------------
        # 1. Resolve company
        # --------------------------------------------

        company = company_resolver.resolve(
            db=db,
            symbol=symbol,
        )

        if conversation_id is not None:
        
            conversation = company_conversation_validator.validate(
                db=db,
                conversation_id=conversation_id,
                company_id=company.id,
            )

        else:

            conversation = (
                company_conversation_service.get_or_create(
                    db=db,
                    company=company,
                    conversation_id=None,
                )
            )


        # --------------------------------------------
        # 2. Resolve/create conversation
        # --------------------------------------------

        conversation = (
            company_conversation_service.get_or_create(
                db=db,
                company=company,
                conversation_id=conversation_id,
            )
        )

        # --------------------------------------------
        # 3. Load conversation memory
        # --------------------------------------------

        memory_limit = 10

        if conversation.settings:
            memory_limit = conversation.settings.get(
                "memory_limit",
                10,
            )

        history = memory_service.get_recent_history(
            session_id=conversation.id,
            limit=memory_limit,
        )

        # --------------------------------------------
        # 4. Classify question
        # --------------------------------------------

        resolved_question = followup_resolver.resolve(
            question=question,
            history=history,
            company_symbol=company.symbol,
        )

        question_type = question_classifier.classify(
            resolved_question.resolved_question,
        )

        financial_context = None
        news_context = None
        sentiment_context = None
        recommendation_context = None

        # --------------------------------------------
        # 5. Retrieve financial context
        # --------------------------------------------

        if question_type in (
            CompanyQuestionType.FINANCIAL,
            CompanyQuestionType.HYBRID,
        ):
            financial_context = (
                financial_context_retriever.retrieve(
                    db=db,
                    company_id=company.id,
                )
            )

        # --------------------------------------------
        # News context
        # --------------------------------------------

        if question_type in (
            CompanyQuestionType.NEWS,
            CompanyQuestionType.HYBRID,
        ):
            news_context = (
                news_context_retriever.retrieve(
                    db=db,
                    company_id=company.id,
                    limit=10,
                )
            )

        # --------------------------------------------
        # Sentiment context
        # --------------------------------------------

        if question_type in (
            CompanyQuestionType.SENTIMENT,
            CompanyQuestionType.HYBRID,
        ):

            sentiment_context = (
                sentiment_context_retriever.retrieve(
                    db=db,
                    company_id=company.id,
                    limit=100,
                )
            )

        # --------------------------------------------
        # Recommendation context
        # --------------------------------------------

        if question_type in (
            CompanyQuestionType.RECOMMENDATION,
            CompanyQuestionType.HYBRID,
        ):

            recommendation_context = (
                recommendation_context_retriever.retrieve(
                    db=db,
                    company_id=company.id,
                )
            )

        # --------------------------------------------
        # 6. Build company context
        # --------------------------------------------

        context = company_context_builder.build(
            company=company,
            question=question,
            question_type=question_type,
            conversation=history,
            resolved_question=resolved_question.resolved_question,
            financial=financial_context,
            news=news_context,
            sentiment=sentiment_context,
            recommendation=recommendation_context,
        )
        hybrid_context = hybrid_context_builder.build(
            context,
        )

        try:
            answer = (
                company_chat_response_generator.generate(
                    hybrid_context,
                )
            )

        except Exception as exc:
            print(
                "COMPANY CHAT ERROR:",
                repr(exc),
            )
            
            raise CompanyChatProcessingError(
                "Failed to generate company chat response."
            ) from exc
        
        sources = (
            company_chat_source_builder.build(
                hybrid_context,
            )
        )

        self.save_user_message(
            conversation_id=conversation.id,
            message=question,
        )

        self.save_assistant_message(
            conversation_id=conversation.id,
            message=answer,
            citations=sources,
        )

        return {
            "conversation_id": conversation.id,
            "company": {
                "id": company.id,
                "symbol": company.symbol,
                "name": company.company_name,
            },
            "answer": answer,
            "sources": sources,
        }
    
    # -----------------------------------------------------
    # Company resolution
    # -----------------------------------------------------

    def resolve_company(
        self,
        db: Session,
        symbol: str,
    ):
        return company_resolver.resolve(
            db=db,
            symbol=symbol,
        )

    # -----------------------------------------------------
    # Save user message
    # -----------------------------------------------------

    def save_user_message(
        self,
        conversation_id: int,
        message: str,
    ):
        return conversation_service.add_user_message(
            session_id=conversation_id,
            message=message,
        )

    # -----------------------------------------------------
    # Save assistant message
    # -----------------------------------------------------

    def save_assistant_message(
        self,
        conversation_id: int,
        message: str,
        citations: list | None = None,
    ):
        return conversation_service.add_assistant_message(
            session_id=conversation_id,
            message=message,
            citations=citations or [],
        )


    def get_conversation(
        self,
        db: Session,
        company_id: int,
        conversation_id: int,
    ):
        return company_conversation_service.get(
            db=db,
            company_id=company_id,
            conversation_id=conversation_id,
        )

    def list_conversations(
        self,
        db: Session,
        company_id: int,
    ):
        return company_conversation_service.list(
            db=db,
            company_id=company_id,
        )

    def validate_conversation(
        self,
        db: Session,
        company_id: int,
        conversation_id: int,
    ):
        return company_conversation_service.validate(
            db=db,
            company_id=company_id,
            conversation_id=conversation_id,
        )

    def get_messages(
        self,
        db: Session,
        conversation_id: int,
    ):
        return company_conversation_service.get_messages(
            db=db,
            conversation_id=conversation_id,
        )

    
company_chat_service = CompanyChatService()