from pathlib import Path

PROMPT_DIRECTORY = (
    Path(__file__).resolve().parents[2]
    / "ai"
    / "prompts"
)


def load_prompt(filename: str) -> str:
    path = PROMPT_DIRECTORY / filename

    if not path.exists():
        raise FileNotFoundError(path)

    return path.read_text(
        encoding="utf-8"
    )