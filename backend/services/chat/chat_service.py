from fastapi import HTTPException, status

from backend.services.chat.retriever import retriever
from backend.services.chat.context_builder import context_builder
from backend.services.chat.prompt_builder import prompt_builder
from backend.services.llm.gemini_service import gemini_service


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


chat_service = ChatService()