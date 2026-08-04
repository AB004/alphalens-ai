from backend.services.chat.retriever import retriever

results = retriever.retrieve(
    document_ids=[1],
    query="What is the revenue growth?",
    top_k=5,
)

for result in results:
    print(result)