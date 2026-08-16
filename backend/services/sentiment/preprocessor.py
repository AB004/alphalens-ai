import re


class SentimentPreprocessor:
    """
    Prepares financial news text for sentiment analysis.

    The preprocessor is responsible for:
    - combining title, summary, and content
    - cleaning whitespace
    - removing unnecessary HTML
    - handling missing fields
    - limiting input length
    """

    DEFAULT_MAX_CHARACTERS = 4000

    def __init__(
        self,
        max_characters: int = DEFAULT_MAX_CHARACTERS,
    ):
        if max_characters <= 0:
            raise ValueError(
                "max_characters must be greater than zero."
            )

        self.max_characters = max_characters

    def _clean_text(
        self,
        text: str,
    ) -> str:
        """
        Clean a piece of text.
        """

        if not text:
            return ""

        text = str(text)

        # Remove HTML tags.
        text = re.sub(
            r"<[^>]+>",
            " ",
            text,
        )

        # Normalize whitespace.
        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    def prepare(
        self,
        title: str | None = None,
        summary: str | None = None,
        content: str | None = None,
    ) -> str:
        """
        Build the final text that will be sent to FinBERT.
        """

        parts = []

        title = self._clean_text(
            title or "",
        )

        summary = self._clean_text(
            summary or "",
        )

        content = self._clean_text(
            content or "",
        )

        if title:
            parts.append(title)

        if summary:
            parts.append(summary)

        if content:
            parts.append(content)

        if not parts:
            raise ValueError(
                "News article does not contain "
                "usable text for sentiment analysis."
            )

        text = ". ".join(parts)

        return text[:self.max_characters]