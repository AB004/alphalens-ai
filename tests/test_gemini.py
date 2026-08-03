from backend.services.llm.gemini_service import gemini_service

print(
    gemini_service.generate(
        "Say hello."
    )
)