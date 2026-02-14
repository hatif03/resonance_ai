"""LLM client - Bedrock (primary) or Ollama (fallback)."""

import json
from abc import ABC, abstractmethod

from app.config import settings


class LLMClient(ABC):
    """Abstract LLM client interface."""

    @abstractmethod
    async def analyze_transcript(self, transcript: str, system_prompt: str) -> dict:
        """Analyze a transcript and return structured JSON."""
        pass


class BedrockLLMClient(LLMClient):
    """AWS Bedrock client using Mistral/Llama."""

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            import boto3
            from botocore.config import Config
            self._client = boto3.client(
                "bedrock-runtime",
                region_name=settings.aws_region,
                config=Config(retries={"max_attempts": 3, "mode": "standard"}),
            )
        return self._client

    async def analyze_transcript(self, transcript: str, system_prompt: str) -> dict:
        """Analyze transcript using Bedrock Converse API."""
        import asyncio

        def _invoke():
            client = self._get_client()
            response = client.converse(
                modelId=settings.bedrock_model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": f"{system_prompt}\n\n---\n\nTranscript:\n{transcript}",
                            }
                        ],
                    }
                ],
                inferenceConfig={
                    "maxTokens": 2048,
                    "temperature": 0.2,
                    "topP": 0.9,
                },
            )
            output = response["output"]["message"]["content"][0]["text"]
            return output

        loop = asyncio.get_event_loop()
        output = await loop.run_in_executor(None, _invoke)
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
    return BedrockLLMClient()
