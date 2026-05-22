import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")


class Settings(BaseSettings):
    app_name: str = Field(default="MEEYG", validation_alias="APP_NAME")
    app_version: str = Field(default="1.0.0", validation_alias="APP_VERSION")
    db_path: Path = Field(
        default=PROJECT_ROOT / "data" / "meeyg.db",
        validation_alias="DB_PATH",
    )
    db_key: str = Field(
        default="",
        validation_alias="DB_KEY",
    )
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    data_dir: Path = Field(default=PROJECT_ROOT / "data")
    logs_dir: Path = Field(default=PROJECT_ROOT / "logs")

    @field_validator("db_key", mode="before")
    @classmethod
    def validate_db_key(cls, v: str) -> str:
        if v and len(v) != 64:
            raise ValueError("DB_KEY must be a 64-character hex string (32 bytes)")
        return v

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()
