"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_name: str = "Resonance AI - Call Monitoring"
    debug: bool = False

    # Database (Supabase PostgreSQL)
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/resonance_ai"

    # AWS Bedrock
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "mistral.mistral-7b-instruct-v0:2"

    # LLM provider: bedrock | ollama
    llm_provider: str = "bedrock"
    ollama_base_url: str = "http://localhost:11434/v1"

    # Whisper
    whisper_model_size: str = "base"

    # CORS
    cors_origins: list[str] = ["*"]

    # Google Meet (optional)
    google_credentials_path: str | None = None

    # Twilio - base URL for WebSocket (e.g. wss://api.example.com)
    twilio_ws_base_url: str = "wss://localhost:8000"


settings = Settings()
