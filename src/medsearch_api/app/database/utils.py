from sqlalchemy import create_engine, exc as sqlalchemy_exc, text
from sqlalchemy.engine import Connection, Engine
import logging
from medsearch_api.app.config import settings

logger = logging.getLogger(__name__)


class DatabaseConfigurationException(Exception):
    def __init__(self, message):
        super().__init__(message)


def create_app_user_engine() -> Engine:
    """
    Creates a SQLAlchemy engine for the app user.

    Returns:
        Engine: The SQLAlchemy engine for the app user.
    """
    uri = f"mysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}"
    return create_engine(uri)


def app_database_exists(conn: Connection) -> bool:
    """
    Checks if the specified database exists.

    Args:
        conn (Connection): The SQLAlchemy connection.

    Returns:
        bool: True if the database exists, False otherwise.
    """
    result = conn.execute(
        text(
            f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{settings.MYSQL_DATABASE}'"
        )
    )
    exists = result.fetchone() is not None
    return exists


def verify_database() -> None:
    """
    Verifies if the app database exists and raises an error if not found.

    Raises:
        DatabaseConfigurationException: If the database schema is not found.
    """
    try:
        engine = create_app_user_engine()
        with engine.connect() as conn:
            db_exists = app_database_exists(conn)

            if not db_exists:
                raise DatabaseConfigurationException("Database schema not found.")
    except sqlalchemy_exc.SQLAlchemyError as e:
        logger.error(f"Error connecting as app user: {e}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during database verification: {e}")
        raise e
