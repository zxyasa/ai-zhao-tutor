from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: Optional[str] = None
    sqlite_fallback: str = "sqlite:///./mathcoach.db"
    api_title: str = "MathCoach API"
    api_version: str = "0.1.0"
    debug: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def db_url(self) -> str:
        return self.database_url or self.sqlite_fallback


settings = Settings()
