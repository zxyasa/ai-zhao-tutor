from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    environment: str = "development"
    database_url: Optional[str] = None
    sqlite_fallback: str = f"sqlite:///{(Path(__file__).resolve().parents[1] / 'mathcoach.db').as_posix()}"
    api_title: str = "MathCoach API"
    api_version: str = "0.1.0"
    debug: bool = True
    secret_key: str = "change-me-in-production"
    openai_api_key: Optional[str] = None
    send_parent_email_on_student_create: bool = False
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_sender: Optional[str] = None
    smtp_use_tls: bool = True
    email_retry_attempts: int = 2
    token_expire_minutes: int = 60 * 24 * 7
    cors_origins_raw: str = (
        "http://localhost:3000,"
        "http://127.0.0.1:3000,"
        "http://localhost:5173,"
        "http://127.0.0.1:5173,"
        "http://localhost:8000,"
        "http://127.0.0.1:8000"
    )

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @property
    def db_url(self) -> str:
        return self.database_url or self.sqlite_fallback

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in {"production", "prod"}

    def production_validation_errors(self) -> list[str]:
        errors: list[str] = []
        if not self.is_production:
            return errors

        if self.secret_key == "change-me-in-production":
            errors.append("SECRET_KEY is still using the default placeholder value.")
        if len(self.secret_key) < 32:
            errors.append("SECRET_KEY must be at least 32 characters in production.")
        if self.debug:
            errors.append("DEBUG must be false in production.")

        localhost_origins = [
            origin for origin in self.cors_origins
            if "localhost" in origin or "127.0.0.1" in origin
        ]
        if localhost_origins:
            errors.append(
                "CORS contains localhost origins in production: "
                + ", ".join(localhost_origins)
            )

        return errors

    def validate_runtime(self) -> None:
        errors = self.production_validation_errors()
        if not errors:
            return
        message = "Production configuration validation failed:\n- " + "\n- ".join(errors)
        raise RuntimeError(message)


settings = Settings()
