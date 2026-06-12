import os
from typing import List
from pydantic import AnyHttpUrl, BeforeValidator, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    PROJECT_NAME: str = "SSH Manager Pro"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "supersecretkeychangeinproduction1234567890"  # Change in production!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENCRYPTION_KEY: str = "32bytekeyforfernetencryption_mustbe32bytes="  # Change in production! Fernet key

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "ssh_manager"
    
    SQLALCHEMY_DATABASE_URI: str | None = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, values: any) -> any:
        if isinstance(v, str):
            return v
        
        # Access raw data using the values dictionary if available or settings fields
        data = values.data
        server = data.get("POSTGRES_SERVER")
        
        # Fallback to SQLite for local development/debugging without Postgres
        if server == "sqlite" or os.getenv("USE_SQLITE") == "true":
            return "sqlite+aiosqlite:///ssh_manager.db"
            
        port = data.get("POSTGRES_PORT")
        user = data.get("POSTGRES_USER")
        password = data.get("POSTGRES_PASSWORD")
        db = data.get("POSTGRES_DB")
        
        return f"postgresql+asyncpg://{user}:{password}@{server}:{port}/{db}"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # ACME Settings
    ACME_DIRECTORY_URL: str = "https://acme-staging-v02.api.letsencrypt.org/directory"
    ACME_ACCOUNT_EMAIL: str = "admin@example.com"

    # Agent Secret
    AGENT_SHARED_SECRET: str = "agentsharedsecretforauthandencryption"


settings = Settings()
