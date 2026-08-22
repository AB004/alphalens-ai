from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from backend.database.session import SessionLocal

from backend.schemas.company_chat import (
    CompanyChatRequest,
    CompanyChatResponse,
    CompanyConversationResponse,
)

from backend.services.company_chat.company_chat_service import (
    company_chat_service,
)

from backend.services.company_chat.exceptions import (
    CompanyChatError,
    CompanyNotFoundError,
    EmptyQuestionError,
    ConversationNotFoundError,
    InvalidConversationError,
)


router = APIRouter(
    tags=["Company Chat"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

@router.post(
    "/{symbol}/chat",
    response_model=CompanyChatResponse,
)
def company_chat(
    symbol: str,
    request: CompanyChatRequest,
    db: Session = Depends(get_db),
):
    """
    Ask a question about a company.

    The conversation is created automatically
    when conversation_id is not provided.
    """

    symbol = symbol.strip().upper()

    try:

        result = company_chat_service.process_question(
            db=db,
            symbol=symbol,
            question=request.message,
            conversation_id=request.conversation_id,
        )

        return {
            "conversation_id": result["conversation_id"],
            "symbol": result["company"]["symbol"],
            "company_name": result["company"]["name"],
            "answer": result["answer"],
            "sources": result["sources"],
        }

    except EmptyQuestionError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except CompanyNotFoundError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except ConversationNotFoundError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except InvalidConversationError as exc:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    except CompanyChatError as exc:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    except Exception as exc:

        print(
            "COMPANY CHAT ERROR:",
            repr(exc),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

@router.get(
    "/{symbol}/chat/{conversation_id}",
    response_model=CompanyConversationResponse,
)
def get_company_conversation(
    symbol: str,
    conversation_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve a company conversation.
    """

    symbol = symbol.strip().upper()

    try:

        company = company_chat_service.resolve_company(
            db=db,
            symbol=symbol,
        )

        conversation = (
            company_chat_service.get_conversation(
                db=db,
                company_id=company.id,
                conversation_id=conversation_id,
            )
        )

        return conversation

    except CompanyNotFoundError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except ConversationNotFoundError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except InvalidConversationError as exc:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

@router.get(
    "/{symbol}/chats",
)
def list_company_conversations(
    symbol: str,
    db: Session = Depends(get_db),
):
    """
    Return all conversations for a company.
    """

    symbol = symbol.strip().upper()

    try:

        company = company_chat_service.resolve_company(
            db=db,
            symbol=symbol,
        )

        conversations = (
            company_chat_service.list_conversations(
                db=db,
                company_id=company.id,
            )
        )

        return {
            "symbol": company.symbol,
            "conversations": conversations,
        }

    except CompanyNotFoundError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

@router.get(
    "/{symbol}/chat/{conversation_id}/messages",
)
def get_company_chat_messages(
    symbol: str,
    conversation_id: int,
    db: Session = Depends(get_db),
):
    symbol = symbol.strip().upper()

    try:

        company = company_chat_service.resolve_company(
            db=db,
            symbol=symbol,
        )

        company_chat_service.validate_conversation(
            db=db,
            company_id=company.id,
            conversation_id=conversation_id,
        )

        messages = (
            company_chat_service.get_messages(
                db=db,
                conversation_id=conversation_id,
            )
        )

        return {
            "conversation_id": conversation_id,
            "symbol": company.symbol,
            "messages": messages,
        }

    except CompanyNotFoundError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except InvalidConversationError as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    except ConversationNotFoundError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )