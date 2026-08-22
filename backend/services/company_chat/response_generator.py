
from backend.services.company_chat.company_chat_prompt_builder import (
    company_chat_prompt_builder,
)

from backend.services.llm.gemini_service import (
    gemini_service,
)


class CompanyChatResponseGenerator:
    """
    Generate the final answer for Company Chat.

    Responsibilities:
    - Build the final prompt.
    - Call the LLM.
    - Validate the response.
    - Return the generated answer.
    """

    def generate(
        self,
        context: dict,
    ) -> str:

        prompt = (
            company_chat_prompt_builder.build(
                context,
            )
        )

        answer = gemini_service.generate_text(
            prompt=prompt,
            temperature=0.2,
        )

        if answer is None:
            raise RuntimeError(
                "LLM returned no response."
            )

        answer = answer.strip()

        if not answer:
            raise RuntimeError(
                "LLM returned an empty response."
            )

        return answer


company_chat_response_generator = (
    CompanyChatResponseGenerator()
)