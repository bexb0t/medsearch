import pytest
from unittest.mock import MagicMock, patch
import sqlalchemy.exc as sqlalchemy_exc
from sqlalchemy.engine import Connection
from medsearch_api.app.database.utils import (
    app_database_exists,
    verify_database,
    DatabaseConfigurationException,
)


class TestAppDatabaseExists:
    def test_returns_true_if_schema_found(self):

        conn = MagicMock(spec=Connection)
        conn.execute.return_value.fetchone.return_value = ("test_db",)

        exists = app_database_exists(conn)

        assert exists is True

    def test_returns_false_if_schema_not_found(self):

        conn = MagicMock(spec=Connection)
        conn.execute.return_value.fetchone.return_value = None

        exists = app_database_exists(conn)

        assert exists is False

    def test_raises_if_exception(self):

        conn = MagicMock(spec=Connection)
        conn.execute.side_effect = sqlalchemy_exc.SQLAlchemyError

        with pytest.raises(sqlalchemy_exc.SQLAlchemyError):
            app_database_exists(conn)


class TestVerifyDatabase:
    @patch("medsearch_api.app.database.utils.create_app_user_engine")
    @patch("medsearch_api.app.database.utils.app_database_exists")
    def test_succeeds_if_conn_succeeds_and_db_exists(
        self, mock_app_db_exists, mock_create_engine
    ):

        engine = MagicMock()
        mock_create_engine.return_value = engine
        mock_app_db_exists.return_value = True

        try:
            verify_database()
        except Exception:
            pytest.fail("verify_database() raised Exception unexpectedly!")

        mock_create_engine.assert_called_once()
        mock_app_db_exists.assert_called_once_with(engine.connect().__enter__())

    @patch("medsearch_api.app.database.utils.create_app_user_engine")
    @patch("medsearch_api.app.database.utils.app_database_exists")
    def test_raises_database_config_exception_if_db_not_found(
        self, mock_app_db_exists, mock_create_engine
    ):

        engine = MagicMock()
        mock_create_engine.return_value = engine
        mock_app_db_exists.return_value = False

        with pytest.raises(DatabaseConfigurationException):
            verify_database()

    @patch("medsearch_api.app.database.utils.create_app_user_engine")
    def test_raises_sqlalchemy_error(self, mock_create_engine):

        mock_create_engine.side_effect = sqlalchemy_exc.SQLAlchemyError

        with pytest.raises(sqlalchemy_exc.SQLAlchemyError):
            verify_database()

    @patch("medsearch_api.app.database.utils.create_app_user_engine")
    def test_raises_other_exception(self, mock_create_engine):

        mock_create_engine.side_effect = Exception

        with pytest.raises(Exception):
            verify_database()
