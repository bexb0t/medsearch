import logging
import logging.config
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
    MYSQL_LOGGING: bool = bool(os.getenv("MYSQL_LOGGING"))

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

    def configure_logging(self):
        if self.LOGGING_CONFIG.exists():
            print(f"Setting logging config with file: {self.LOGGING_CONFIG}")
            logging.config.fileConfig(self.LOGGING_CONFIG)
        else:
            print(
                "No logging config file found. Loading default logging configuration."
            )
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )


settings = Settings()
settings.configure_logging()

logger = logging.getLogger(__name__)

print(f"Logging level: {logging.getLevelName(logger.getEffectiveLevel())}")


# debugging
logger.debug(f"ENV: {settings.ENV}")
logger.debug(f"MYSQL_HOST: {settings.MYSQL_HOST}")
logger.debug(f"MYSQL_PORT: {settings.MYSQL_PORT}")
logger.debug(f"MYSQL_ADMIN_USER: {settings.MYSQL_ADMIN_USER}")
logger.debug(f"MYSQL_ADMIN_PASSWORD: {settings.MYSQL_ADMIN_PASSWORD}")
logger.debug(f"MYSQL_USER: {settings.MYSQL_USER}")
logger.debug(f"MYSQL_PASSWORD: {settings.MYSQL_PASSWORD}")
logger.debug(f"MYSQL_DATABASE: {settings.MYSQL_DATABASE}")
logger.debug(f"MYSQL_LOGGING: {settings.MYSQL_LOGGING}")
logger.debug(f"Database URI: {settings.SQLALCHEMY_DATABASE_URI}")
