from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str
    INTERNAL_SECRET_KEY: str
    JWT_ALGORITHM: str
    EXPECTED_ISSUER: str
    EXPECTED_AUDIENCE: str
    EXPECTED_SCOPE: str
    ENV: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env", extra="ignore"
    )


settings = Settings()
