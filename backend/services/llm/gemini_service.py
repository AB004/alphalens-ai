import json
from typing import Any

from google import genai
from google.genai.types import GenerateContentConfig

from backend.core.config import settings


class GeminiService:
    """Wrapper around the Gemini API."""

    def __init__(self) -> None:
        api_key = settings.gemini_api_key

        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured.")

        self.client = genai.Client(api_key=api_key)

        self.model = settings.gemini_model

    def generate_text(
        self,
        prompt: str,
        temperature: float = 0.2,
    ) -> str:
        """Generate plain text."""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=GenerateContentConfig(
                temperature=temperature,
            ),
        )

        return response.text.strip()

    def generate_json(
        self,
        prompt: str,
        temperature: float = 0.2,
    ) -> dict[str, Any]:
        """Generate structured JSON."""

        response = self.generate_text(
            prompt=prompt,
            temperature=temperature,
        )

        response = response.strip()

        if response.startswith("```json"):
            response = response[7:]

        if response.startswith("```"):
            response = response[3:]

        if response.endswith("```"):
            response = response[:-3]

        response = response.strip()

        try:
            return json.loads(response)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Gemini returned invalid JSON:\n{response}"
            ) from exc

    def generate_stream(
        self,
        prompt: str,
        temperature: float = 0.2,
    ):
        """Stream generated text."""

        stream = self.client.models.generate_content_stream(
            model=self.model,
            contents=prompt,
            config=GenerateContentConfig(
                temperature=temperature,
            ),
        )

        for chunk in stream:
            if chunk.text:
                yield chunk.text


gemini_service = GeminiService()
