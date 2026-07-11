from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "DocuFlow AI"

    # Database Configuration
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres_secure_password"
    POSTGRES_DB: str = "docuflow_db"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432

    # Connection URL (resolved dynamically if not explicit)
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres_secure_password@postgres:5432/docuflow_db"
    )

    # Embedding Provider Configuration
    EMBEDDING_PROVIDER: str = Field(
        default="fastembed", description="Embedding provider: 'fastembed' or 'openai'"
    )
    OPENAI_EMBEDDING_MODEL: str = Field(
        default="text-embedding-3-small", description="Model name for OpenAI embeddings"
    )
    FASTEMBED_MODEL: str = Field(
        default="BAAI/bge-small-en-v1.5",
        description="Model name for local FastEmbed embeddings",
    )

    # API Keys & Third-party configs
    OPENAI_API_KEY: str | None = None

    # Storage Configuration
    UPLOAD_DIR: str = "/app/uploads"


settings = Settings()
