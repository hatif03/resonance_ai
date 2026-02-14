"""LLM client - Gemini (primary) or Ollama (fallback)."""

import json
from abc import ABC, abstractmethod

from app.config import settings


class LLMClient(ABC):
    """Abstract LLM client interface."""

    @abstractmethod
    async def analyze_transcript(self, transcript: str, system_prompt: str) -> dict:
        """Analyze a transcript and return structured JSON."""
        pass


class GeminiLLMClient(LLMClient):
    """Google Gemini API client (free tier available)."""

    async def analyze_transcript(self, transcript: str, system_prompt: str) -> dict:
        """Analyze transcript using Gemini API."""
        import httpx

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent"

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                url,
                params={"key": settings.gemini_api_key},
                json={
                    "contents": [
                        {
                            "parts": [
                                {"text": f"{system_prompt}\n\n---\n\nTranscript:\n{transcript}"}
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.2,
                        "topP": 0.9,
                        "maxOutputTokens": 2048,
                    },
                },
            )
            response.raise_for_status()
            data = response.json()
            output = data["candidates"][0]["content"]["parts"][0]["text"]
            return _parse_json_output(output)


class OllamaLLMClient(LLMClient):
    """Ollama client for local Mistral/Llama."""

    async def analyze_transcript(self, transcript: str, system_prompt: str) -> dict:
        """Analyze transcript using Ollama API."""
        import httpx

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.ollama_base_url.rstrip('/')}/chat/completions",
                json={
                    "model": "mistral",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Transcript:\n{transcript}"},
                    ],
                    "temperature": 0.2,
                    "max_tokens": 2048,
                },
            )
            response.raise_for_status()
            data = response.json()
            output = data["choices"][0]["message"]["content"]
            return _parse_json_output(output)


def _parse_json_output(text: str) -> dict:
    """Extract JSON from LLM output (may be wrapped in markdown)."""
    text = text.strip()
    if "```json" in text:
        start = text.find("```json") + 7
        end = text.find("```", start)
        text = text[start:end]
    elif "```" in text:
        start = text.find("```") + 3
        end = text.find("```", start)
        text = text[start:end]
    return json.loads(text)


def get_llm_client() -> LLMClient:
    """Get LLM client based on config."""
    if settings.llm_provider == "ollama":
        return OllamaLLMClient()
    return GeminiLLMClient()
