"""Manual retriever smoke test; excluded from pytest collection side effects."""


def main() -> None:
    from backend.services.document_chat.document_retriever import document_retriever

    results = document_retriever.retrieve(
        document_ids=[1],
        query="What is the revenue growth?",
        top_k=5,
    )
    for result in results:
        print(result)


if __name__ == "__main__":
    main()
