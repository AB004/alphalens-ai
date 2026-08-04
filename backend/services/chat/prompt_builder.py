from backend.utils.prompt_loader import load_prompt


class PromptBuilder:
    """
    Builds the final prompt sent to the LLM.
    """

    def __init__(self):
        self.template = load_prompt("chat.txt")

    def build(
        self,
        context: str,
        question: str,
    ) -> str:
        """
        Build the final LLM prompt.
        """

        return (
            self.template
            .replace(
                "{context}",
                context,
            )
            .replace(
                "{question}",
                question,
            )
        )


prompt_builder = PromptBuilder()