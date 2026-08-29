from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    SECRET_KEY: str
    TMDB_API_KEY: str
    DATABASE_URL: str
    GOOGLE_BOOKS_API_KEY: str
    IGDB_CLIENT_ID: str
    IGDB_CLIENT_SECRET_KEY: str

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env"
    )


settings = Settings()