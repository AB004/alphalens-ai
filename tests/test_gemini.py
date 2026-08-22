"""Manual Gemini smoke test; excluded from pytest collection side effects."""


def main() -> None:
    from backend.services.llm.gemini_service import gemini_service

    print(gemini_service.generate_text("Say hello."))


if __name__ == "__main__":
    main()
