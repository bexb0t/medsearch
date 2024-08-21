from unittest.mock import MagicMock, patch
from sqlalchemy import Column, Integer, String, UniqueConstraint, inspect

from medsearch_api.app.database.db_client import DBClient


class TestModel:
    __tablename__ = "test_model"
    id = Column(Integer, primary_key=True)
    unique_field = Column(String, unique=True)


class TestGetFilterCriteriaForUniqueKeys:
    @patch("sqlalchemy.create_engine")
    def test_single_unique_constraint(self, mock_create_engine):
        mock_engine_instance = MagicMock()
        mock_inspector = MagicMock(spec=inspect)
        mock_inspector.unique_constraints = [UniqueConstraint("unique_field")]
        mock_engine_instance.inspect.return_value = mock_inspector

        mock_create_engine.return_value = mock_engine_instance

        data_access = DBClient()  # Assuming DataAccess is your class
        model_instance = TestModel()
        result = data_access._get_filter_criteria_for_unique_keys(model_instance)

        assert result == {"unique_field": model_instance.unique_field}
