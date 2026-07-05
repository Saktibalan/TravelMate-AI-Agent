"""
Central configuration for TravelMate AI.
All secrets are loaded from environment variables — never hardcode keys.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # LLM
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "claude-sonnet-4-6")

    # External travel APIs
    AMADEUS_API_KEY: str = os.getenv("AMADEUS_API_KEY", "")
    AMADEUS_API_SECRET: str = os.getenv("AMADEUS_API_SECRET", "")
    GOOGLE_PLACES_API_KEY: str = os.getenv("GOOGLE_PLACES_API_KEY", "")
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")
    BOOKING_API_KEY: str = os.getenv("BOOKING_API_KEY", "")

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://user:password@localhost:5432/travelmate"
    )
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_store")

    # App
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = ENV == "development"


settings = Settings()


def validate_settings() -> list[str]:
    """Returns a list of missing required env vars. Call this at startup."""
    required = {
        "ANTHROPIC_API_KEY": settings.ANTHROPIC_API_KEY,
        "AMADEUS_API_KEY": settings.AMADEUS_API_KEY,
        "GOOGLE_PLACES_API_KEY": settings.GOOGLE_PLACES_API_KEY,
    }
    return [name for name, value in required.items() if not value]
