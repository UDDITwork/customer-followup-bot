"""
Configuration module with environment detection.
Supports both local (mock emails) and production (Resend) modes.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Environment mode
    environment: str = "local"  # "local" or "production"

    # Turso Database
    turso_database_url: str
    turso_auth_token: str

    # Claude API
    anthropic_api_key: str

    # Resend API (production only)
    resend_api_key: Optional[str] = None
    resend_from_email: Optional[str] = None

    # App Config
    frontend_url: str = "http://localhost:5173"
    port: int = 8000

    class Config:
        # Load from .env.local or .env.production based on ENVIRONMENT variable
        env_file = ".env.local"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"

    @property
    def is_local(self) -> bool:
        """Check if running in local/development mode."""
        return self.environment.lower() == "local"


# Determine which env file to load based on ENVIRONMENT variable
env = os.getenv("ENVIRONMENT", "local").lower()
env_file = ".env.production" if env == "production" else ".env.local"

settings = Settings(_env_file=env_file)
