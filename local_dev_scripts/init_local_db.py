import os
from sqlalchemy import create_engine, text

# Retrieve environment variables
MYSQL_ROOT_USER = os.getenv("MYSQL_ROOT_USER", "root")
MYSQL_ROOT_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_ADMIN_USER = os.getenv("MYSQL_ADMIN_USER")
MYSQL_ADMIN_PASSWORD = os.getenv("MYSQL_ADMIN_PASSWORD")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")


def check_env_vars():
    required_vars = [
        "MYSQL_ROOT_PASSWORD",
        "MYSQL_HOST",
        "MYSQL_PORT",
        "MYSQL_DATABASE",
        "MYSQL_ADMIN_USER",
        "MYSQL_ADMIN_PASSWORD",
        "MYSQL_USER",
        "MYSQL_PASSWORD",
    ]
    for var in required_vars:
        if not os.getenv(var):
            raise ValueError(f"Environment variable {var} is not set.")


def create_root_connection():
    root_uri = (
        f"mysql://{MYSQL_ROOT_USER}:{MYSQL_ROOT_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}"
    )
    return create_engine(root_uri)


def create_database_if_not_exists(conn):
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DATABASE}`;"))
    print(f"Created database '{MYSQL_DATABASE}'.")


def create_admin_user_if_not_exists(conn):
    conn.execute(
        text(
            f"CREATE USER IF NOT EXISTS '{MYSQL_ADMIN_USER}'@'%' IDENTIFIED BY '{MYSQL_ADMIN_PASSWORD}'"
        )
    )
    print(f"Created admin user '{MYSQL_ADMIN_USER}'.")
    conn.execute(
        text(
            f"GRANT CREATE, ALTER, DROP, INSERT, UPDATE, DELETE, SELECT, INDEX, REFERENCES ON `{MYSQL_DATABASE}`.* TO '{MYSQL_ADMIN_USER}'@'%'"
        )
    )
    conn.execute(text("FLUSH PRIVILEGES"))
    print(
        f"Granted privileges on database '{MYSQL_DATABASE}' to admin user '{MYSQL_ADMIN_USER}'."
    )


def create_app_user_if_not_exists(conn):
    conn.execute(
        text(
            f"CREATE USER IF NOT EXISTS '{MYSQL_USER}'@'%' IDENTIFIED BY '{MYSQL_PASSWORD}'"
        )
    )
    print(f"Created app user '{MYSQL_USER}'.")
    conn.execute(
        text(
            f"GRANT SELECT, INSERT, DELETE, UPDATE, CREATE TEMPORARY TABLES, EXECUTE ON `{MYSQL_DATABASE}`.* TO '{MYSQL_USER}'@'%'"
        )
    )
    conn.execute(text("FLUSH PRIVILEGES"))
    print(
        f"Granted privileges on app database '{MYSQL_DATABASE}' to user '{MYSQL_USER}'."
    )


def init_local_db():
    engine = create_root_connection()
    print("Connection created.")
    with engine.connect() as conn:
        create_database_if_not_exists(conn)
        create_admin_user_if_not_exists(conn)
        create_app_user_if_not_exists(conn)


if __name__ == "__main__":
    check_env_vars()
    init_local_db()
