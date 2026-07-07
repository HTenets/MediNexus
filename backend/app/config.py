from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = ""
    redis_url: str = ""
    qdrant_url: str = ""
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    demo_mode: bool = True
    allowed_origins: str = "*"

    model_config = {"env_file": ".env", "env_prefix": "MEDINEXUS_"}


settings = Settings()
