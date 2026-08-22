from backend.utils.prompt_loader import load_prompt


class PromptBuilder:
    """
    Builds the final prompt sent to the LLM.
    """

    def __init__(self):
        self.template = load_prompt("chat.txt")

    def build(
        self,
        history: str,
        context: str,
        question: str,
    ) -> str:
        """
        Build the final LLM prompt.
        """

        return (
            self.template
            .replace("{history}", history)
            .replace("{context}", context)
            .replace("{question}", question)
        )


prompt_builder = PromptBuilder()