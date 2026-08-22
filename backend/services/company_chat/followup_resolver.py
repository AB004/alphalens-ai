from dataclasses import dataclass


@dataclass
class ResolvedQuestion:
    """
    Result of resolving a user's question
    against previous conversation context.
    """

    original_question: str

    resolved_question: str

    is_follow_up: bool


class FollowUpResolver:
    """
    Resolve short or ambiguous follow-up questions
    using conversation history.

    This is intentionally deterministic.

    It does not call the LLM.
    """

    FOLLOW_UP_STARTERS = {
        "what about",
        "how about",
        "what was",
        "what is",
        "what are",
        "and",
        "also",
        "why",
        "how",
        "when",
        "where",
        "which",
        "can you explain",
        "tell me more",
    }

    PRONOUNS = {
        "it",
        "its",
        "they",
        "their",
        "them",
        "this",
        "that",
        "these",
        "those",
    }

    def resolve(
        self,
        question: str,
        history: list[dict] | None,
        company_symbol: str,
    ) -> ResolvedQuestion:

        question = question.strip()

        if not history:
            return ResolvedQuestion(
                original_question=question,
                resolved_question=question,
                is_follow_up=False,
            )

        if not self._is_follow_up(question):
            return ResolvedQuestion(
                original_question=question,
                resolved_question=question,
                is_follow_up=False,
            )

        resolved_question = self._add_company_context(
            question=question,
            company_symbol=company_symbol,
        )

        return ResolvedQuestion(
            original_question=question,
            resolved_question=resolved_question,
            is_follow_up=True,
        )

    def _is_follow_up(
        self,
        question: str,
    ) -> bool:

        text = question.lower().strip()

        if not text:
            return False

        words = text.split()

        # Explicit pronoun reference.
        if any(
            word.strip("?,.!").lower()
            in self.PRONOUNS
            for word in words
        ):
            return True

        # Explicit follow-up phrases.
        for starter in self.FOLLOW_UP_STARTERS:

            if text.startswith(starter):
                return True

        # Very short contextual questions.
        if len(words) <= 4:
            return True

        return False

    def _add_company_context(
        self,
        question: str,
        company_symbol: str,
    ) -> str:

        return (
            f"Regarding {company_symbol}, "
            f"the user's follow-up question is: "
            f"{question}"
        )


followup_resolver = FollowUpResolver()