from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Django Core
    DEBUG: bool = False
    SECRET_KEY: SecretStr  # Prevents accidental logging of the secret

    # Database
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr  # Hidden in logs/exceptions
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432

    # Redis / Celery / Cache
    CELERY_BROKER_URL: str
    REDIS_URL: str
    RATE_CACHE_KEY: str = "rates_data_latest"

    @property
    def DATABASE_URL(self) -> str:
        # Use .get_secret_value() to access the actual string for the connection
        return (
            f"postgresql://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD.get_secret_value()}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}"
        )


# Initialize
try:
    settings = Settings()
except Exception as e:
    # This will catch if SECRET_KEY or POSTGRES_DB are missing from .env
    print(f"❌ Configuration Error: {e}")
    raise SystemExit(1)
