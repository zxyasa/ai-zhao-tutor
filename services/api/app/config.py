from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    database_url: Optional[str] = None
    sqlite_fallback: str = f"sqlite:///{(Path(__file__).resolve().parents[1] / 'mathcoach.db').as_posix()}"
    api_title: str = "MathCoach API"
    api_version: str = "0.1.0"
    debug: bool = True

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @property
    def db_url(self) -> str:
        return self.database_url or self.sqlite_fallback


settings = Settings()
