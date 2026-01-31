from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the backend directory (where .env lives)
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = "sqlite:///./inspire.db"

    # Encryption (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
    encryption_key: str = "your-fernet-key-here-generate-one"

    # Document Reader Service: "ocr" or "document_ai"
    document_reader_service: str = "document_ai"

    # Google Document AI Configuration (required if document_reader_service=document_ai)
    gcp_project_id: str | None = None
    gcp_location: str = "us"  # "us" or "eu" for Document AI
    document_ai_processor_id: str | None = None  # Identity document processor ID

    # Clerk Authentication
    clerk_secret_key: str | None = None  # sk_test_xxx or sk_live_xxx
    clerk_publishable_key: str | None = None  # pk_test_xxx or pk_live_xxx
    clerk_jwks_url: str | None = None  # Auto-derived if not set

    # OpenRouter LLM Configuration
    openrouter_api_key: str | None = None  # sk-or-v1-xxx
    llm_model: str = "anthropic/claude-3.5-sonnet"  # OpenRouter model identifier

    # Application
    app_env: str = "development"
    debug: bool = True

    # API Keys for service-to-service auth (comma-separated list)
    # These are static API keys that bypass JWT validation
    api_keys: str | None = None

    @property
    def api_keys_list(self) -> list[str]:
        """Parse API keys into a list."""
        if not self.api_keys:
            return []
        return [k.strip() for k in self.api_keys.split(",") if k.strip()]

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def clerk_configured(self) -> bool:
        """Check if Clerk authentication is configured."""
        return self.clerk_secret_key is not None

    @property
    def llm_configured(self) -> bool:
        """Check if LLM (OpenRouter) is configured."""
        return self.openrouter_api_key is not None


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()


settings = get_settings()
