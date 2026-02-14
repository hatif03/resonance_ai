"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "Resonance AI - Call Monitoring"
    debug: bool = False

    # Database – SQLite for local dev, PostgreSQL (Supabase) for production
    database_url: str = "sqlite+aiosqlite:///./resonance.db"

    # Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # LLM provider: gemini | ollama
    llm_provider: str = "gemini"
    ollama_base_url: str = "http://localhost:11434/v1"

    # Whisper
    whisper_model_size: str = "base"

    # CORS (use "*" or comma-separated origins)
    cors_origins: str = "*"

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]



settings = Settings()
