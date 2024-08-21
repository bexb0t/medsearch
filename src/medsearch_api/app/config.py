from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import FilePath
from pydantic.functional_validators import field_validator
import os
from pathlib import Path

# Print the current working directory


class Settings(BaseSettings):
    ENV: Optional[str] = os.getenv("ENV")
    # logging.conf should be in the same directory as config.py
    LOGGING_CONFIG: FilePath = Path(__file__).parent / "logging.conf"
    MYSQL_HOST: Optional[str] = os.getenv("MYSQL_HOST")
    MYSQL_PORT: Optional[int] = int(os.getenv("MYSQL_PORT", default="3306"))
    MYSQL_ADMIN_USER: Optional[str] = os.getenv("MYSQL_ADMIN_USER")
    MYSQL_ADMIN_PASSWORD: Optional[str] = os.getenv("MYSQL_ADMIN_PASSWORD")
    MYSQL_USER: Optional[str] = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD: Optional[str] = os.getenv("MYSQL_PASSWORD")
    MYSQL_DATABASE: Optional[str] = os.getenv("MYSQL_DATABASE")
    MYSQL_LOGGING: bool = True  # bool(os.getenv("MYSQL_LOGGING"))

    # SQLAlchemy env variables
    SQLALCHEMY_DATABASE_URI: Optional[str] = (
        f"mysql://{MYSQL_USER or ''}:{MYSQL_PASSWORD or ''}@{MYSQL_HOST or 'localhost'}:{MYSQL_PORT or 3306}/{MYSQL_DATABASE or ''}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    @field_validator(
        "ENV",
        "MYSQL_HOST",
        "MYSQL_PORT",
        "MYSQL_ADMIN_USER",
        "MYSQL_ADMIN_PASSWORD",
        "MYSQL_USER",
        "MYSQL_PASSWORD",
        "MYSQL_DATABASE",
    )
    @classmethod
    def validate_env_variables(cls, v):
        if v is None or v == "":
            raise ValueError(
                "Must provide a non-empty value for environment variables."
            )
        return v


settings = Settings()
