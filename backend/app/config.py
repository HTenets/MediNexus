import logging
import secrets

from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

_INSECURE_SECRETS = {"", "change-me-in-production", "secret", "jwt_secret"}


class Settings(BaseSettings):
    database_url: str = ""
    redis_url: str = ""
    qdrant_url: str = ""
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    llm_provider: str = "ollama"
    llm_api_key: str = ""
    llm_model: str = ""
    llm_base_url: str = ""
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:14b"
    demo_mode: bool = True
    allowed_origins: str = "*"

    model_config = {"env_file": ".env", "env_prefix": "MEDINEXUS_"}


settings = Settings()

# Ensure JWT secret is secure; generate a random one in demo mode if unset
if settings.jwt_secret in _INSECURE_SECRETS:
    if settings.demo_mode:
        # Auto-generate a random secret for demo/dev so tokens aren't forgeable
        settings.jwt_secret = secrets.token_urlsafe(48)
        logger.warning(
            "JWT secret not configured — generated a random secret for this session. "
            "Set MEDINEXUS_JWT_SECRET in production."
        )
    else:
        raise RuntimeError(
            "MEDINEXUS_JWT_SECRET must be set to a secure random value in production. "
            "The default 'change-me-in-production' is not allowed."
        )
