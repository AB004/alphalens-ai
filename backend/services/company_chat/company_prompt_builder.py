from typing import Any

from backend.utils.prompt_loader import load_prompt


class CompanyChatPromptBuilder:
    """
    Build the final LLM prompt for Company Chat.
    """

    def __init__(self):
        self.template = load_prompt(
            "company_chat.txt"
        )

    def build(
        self,
        context: dict[str, Any],
    ) -> str:

        company = context["company"]

        return self.template.format(
            company_name=company.get(
                "company_name",
                "Not available",
            ),
            symbol=company.get(
                "symbol",
                "Not available",
            ),
            sector=company.get(
                "sector",
                "Not available",
            ),
            industry=company.get(
                "industry",
                "Not available",
            ),
            exchange=company.get(
                "exchange",
                "Not available",
            ),
            currency=company.get(
                "currency",
                "Not available",
            ),
            country=company.get(
                "country",
                "Not available",
            ),

            history=self._build_conversation_history(
                context.get("conversation", [])
            ),

            financial_context=self._format_context(
                context.get("financial")
            ),

            news_context=self._format_context(
                context.get("news")
            ),

            sentiment_context=self._format_context(
                context.get("sentiment")
            ),

            recommendation_context=self._format_context(
                context.get("recommendation")
            ),

            question=context.get(
                "question",
                "",
            ),
            resolved_question=context.get(
                "resolved_question",
                context.get("question", ""),
            ),
        )

    def _build_conversation_history(
        self,
        conversation: list[dict],
    ) -> str:

        if not conversation:
            return "No previous conversation."

        history = []

        for message in conversation:

            role = message.get(
                "role",
                "unknown",
            )

            text = message.get(
                "message",
                "",
            )

            history.append(
                f"{role.capitalize()}: {text}"
            )

        return "\n".join(history)

    def _format_context(
        self,
        value,
    ) -> str:

        if value is None:
            return "No information available."

        if isinstance(value, str):
            return value

        if isinstance(value, dict):

            lines = []

            for key, item in value.items():

                lines.append(
                    f"{key}: {item}"
                )

            return "\n".join(lines)

        if isinstance(value, list):

            if not value:
                return "No information available."

            return "\n".join(
                str(item)
                for item in value
            )

        return str(value)


company_chat_prompt_builder = (
    CompanyChatPromptBuilder()
)