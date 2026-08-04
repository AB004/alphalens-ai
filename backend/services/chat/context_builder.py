from typing import List

MAX_CONTEXT_CHARACTERS = 120000


class ContextBuilder:
    """
    Builds LLM-ready context from retrieved document chunks.
    """

    def __init__(self, max_context_characters: int = MAX_CONTEXT_CHARACTERS):
        self.max_context_characters = max_context_characters

    def build(self, chunks: List[dict]) -> str:
        """
        Convert retrieved chunks into a formatted context string.
        """

        if not chunks:
            return "No relevant document context found."

        chunks = self._remove_duplicates(chunks)

        chunks.sort(
            key=lambda chunk: chunk["score"],
            reverse=True,
        )

        context_sections = []
        current_size = 0

        for chunk in chunks:

            section = self._format_chunk(chunk)

            if current_size + len(section) > self.max_context_characters:
                break

            context_sections.append(section)
            current_size += len(section)

        return "\n".join(context_sections)

    def _format_chunk(self, chunk: dict) -> str:
        """
        Format a single retrieved chunk.
        """

        return (
            "=" * 80
            + "\n"
            + f"Document : {chunk['document_name']}\n"
            + f"Document ID : {chunk['document_id']}\n"
            + f"Page : {chunk['page_number']}\n"
            + f"Similarity : {chunk['score']:.4f}\n\n"
            + chunk["text"].strip()
            + "\n"
        )

    def _remove_duplicates(
        self,
        chunks: List[dict],
    ) -> List[dict]:
        """
        Remove duplicate chunks.
        """

        seen = set()
        unique_chunks = []

        for chunk in chunks:

            key = (
                chunk["document_id"],
                chunk["chunk_id"],
            )

            if key in seen:
                continue

            seen.add(key)
            unique_chunks.append(chunk)

        return unique_chunks


context_builder = ContextBuilder()