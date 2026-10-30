"""Configuration loader for Genome Explorer AI backend."""
import logging
import os
from dataclasses import dataclass, field
from typing import List

logger = logging.getLogger("genome_explorer")


def _parse_cors(raw: str) -> List[str]:
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables or .env."""

    app_name: str = "Genome Explorer AI"
    version: str = "0.1.0-phase1"
    openrouter_api_key: str = field(
        default_factory=lambda: os.getenv("OPENROUTER_API_KEY", "").strip()
    )
    openrouter_model: str = field(
        default_factory=lambda: os.getenv(
            "OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free"
        ).strip()
    )
    openrouter_fallback_model: str = field(
        default_factory=lambda: os.getenv(
            "OPENROUTER_FALLBACK_MODEL", "google/gemma-2-9b-it:free"
        ).strip()
    )
    openrouter_base_url: str = field(
        default_factory=lambda: os.getenv(
            "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
        ).strip()
    )
    cors_origins: List[str] = field(
        default_factory=lambda: _parse_cors(
            os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
        )
    )
    max_file_size_bytes: int = 5 * 1024 * 1024  # 5 MB
    max_sequence_length_bp: int = 100_000

    @property
    def ai_configured(self) -> bool:
        """Return True if a non-placeholder OpenRouter API key is present."""
        return bool(
            self.openrouter_api_key
            and self.openrouter_api_key != "your_openrouter_api_key_here"
        )


def get_settings() -> Settings:
    """Load settings and log a startup warning if OPENROUTER_API_KEY is missing."""
    settings = Settings()
    if not settings.ai_configured:
        logger.warning(
            "OPENROUTER_API_KEY is not set. Core sequence analysis, 3D helix, ORF detection, "
            "and mutation tools remain active; /api/explain will return AI_NOT_CONFIGURED."
        )
    return settings
