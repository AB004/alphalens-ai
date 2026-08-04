from fastapi import HTTPException, status

from backend.database.session import SessionLocal
from backend.services.chat.retriever import retriever
from backend.services.chat.context_builder import context_builder
from backend.services.chat.prompt_builder import prompt_builder
from backend.services.llm.gemini_service import gemini_service
from backend.repositories.conversation_repository import (
    get_session,
)

from backend.services.chat.memory_service import (
    memory_service,
)

from backend.services.chat.conversation_service import (
    conversation_service,
)

class ChatService:

    def chat(
        self,
        document_ids: list[int],
        question: str,
        top_k: int = 10,
    ) -> dict:

        if not question.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question cannot be empty.",
            )

        if not document_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one document id is required.",
            )

        # Step 1
        chunks = retriever.retrieve(
            document_ids=document_ids,
            query=question,
            top_k=top_k,
        )

        # Step 2
        context = context_builder.build(chunks)

        # Step 3
        prompt = prompt_builder.build(
            context=context,
            question=question,
        )

        # Step 4
        answer = gemini_service.generate_text(
            prompt=prompt,
            temperature=0.2,
        )

        # Step 5
        seen = set()

        citations = []

        for chunk in chunks:

            key = (
                chunk["document_id"],
                chunk["page_number"],
            )

            if key in seen:
                continue

            seen.add(key)

            citations.append(
                {
                    "document_id": chunk["document_id"],
                    "document_name": chunk["document_name"],
                    "page_number": chunk["page_number"],
                }
            )

        return {
            "question": question,
            "answer": answer,
            "citations": citations,
        }
    
    def conversation_chat(
        self,
        session_id: int,
        question: str,
    ) -> dict:

        if not question.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question cannot be empty.",
            )

        db = SessionLocal()

        try:

            session = get_session(
                db,
                session_id,
            )

            if session is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found.",
                )

            # -------------------------------
            # Load conversation history
            # -------------------------------

            history = memory_service.build_history(
                session_id=session_id,
            )

            # -------------------------------
            # Retrieve document chunks
            # -------------------------------

            chunks = retriever.retrieve(
                document_ids=session.document_ids,
                query=question,
                top_k=session.settings.get("top_k", 10)
                if session.settings
                else 10,
            )

            # -------------------------------
            # Build document context
            # -------------------------------

            context = context_builder.build(
                chunks,
            )

            # -------------------------------
            # Build final prompt
            # -------------------------------

            prompt = prompt_builder.build(
                history=history,
                context=context,
                question=question,
            )

            # -------------------------------
            # Generate answer
            # -------------------------------

            answer = gemini_service.generate_text(
                prompt=prompt,
                temperature=session.settings.get("temperature", 0.2)
                if session.settings
                else 0.2,
            )

            # -------------------------------
            # Prepare citations
            # -------------------------------

            seen = set()

            citations = []

            for chunk in chunks:

                key = (
                    chunk["document_id"],
                    chunk["page_number"],
                )

                if key in seen:
                    continue

                seen.add(key)

                citations.append(
                    {
                        "document_id": chunk["document_id"],
                        "document_name": chunk["document_name"],
                        "page_number": chunk["page_number"],
                    }
                )

            # -------------------------------
            # Save conversation
            # -------------------------------

            conversation_service.add_user_message(
                session_id=session_id,
                message=question,
            )

            conversation_service.add_assistant_message(
                session_id=session_id,
                message=answer,
                citations=citations,
            )

            return {
                "answer": answer,
                "citations": citations,
            }

        finally:
            db.close()

chat_service = ChatService()