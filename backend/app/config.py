from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://medinexus:medinexus_dev@localhost:5432/medinexus"
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"

    model_config = {"env_file": ".env", "env_prefix": "MEDINEXUS_"}


settings = Settings()
