import logging
from typing import Any, Dict, Optional, List, Type
from sqlalchemy.exc import IntegrityError, DataError
from medsearch_api.app.database.models import MedSearchBaseModel
from medsearch_api.app.db import db

logger = logging.getLogger(__name__)


class DBClient:
    """
    A client for performing database operations.

    This class provides methods to interact with the database, including
    inserting, upserting, and retrieving models, as well as generating
    filter criteria based on model definitions.

    Attributes:
        session (Session): The SQLAlchemy session used for database transactions.
    """

    def __init__(self):
        self.session = db.session

    def insert_model(self, model: MedSearchBaseModel) -> MedSearchBaseModel:
        """
        Inserts a model instance into the database.

        Adds the provided SQLAlchemy model object to the session and commits
        the transaction. If an error occurs, the transaction is rolled back
        and the error is logged.

        Args:
            model (MedSearchBaseModel): The SQLAlchemy model object to insert.

        Returns:
            MedSearchBaseModel: The inserted model instance.

        Raises:
            IntegrityError: If an integrity constraint is violated.
            DataError: If there is a problem with the data.
            Exception: For any unexpected errors.
        """
        try:
            self.session.add(model)
            self.session.commit()
            return model
        except (IntegrityError, DataError) as e:
            # Handle specific database errors
            self.session.rollback()
            logger.error(f"Error inserting model: {e}")
            raise
        except Exception as e:
            # Log unexpected errors for debugging
            self.session.rollback()
            logger.exception(f"Unexpected error inserting model: {e}")
            raise  # Re-raise the exception

    def upsert_model(
        self, model: MedSearchBaseModel, filter_criteria: dict
    ) -> MedSearchBaseModel:
        """
        Inserts or updates a model instance in the database.

        Args:
            model (MedSearchBaseModel): The SQLAlchemy model object to upsert.
            filter_criteria (dict): Dictionary of filter criteria to determine
            whether to insert or update the model.

        Returns:
            MedSearchBaseModel: The upserted model instance.

        Raises:
            IntegrityError: If an integrity constraint is violated.
            DataError: If there is a problem with the data.
            ValueError: If invalid filter criteria are provided.
            Exception: For any unexpected errors.
        """

        try:
            existing_model = (
                self.session.query(model.__class__).filter_by(**filter_criteria).first()
            )

            if existing_model:
                # Update all fields except those used for filtering
                update_fields = [
                    col
                    for col in model.__table__.columns.keys()
                    if col not in filter_criteria.keys()
                ]

                for field in update_fields:
                    setattr(existing_model, field, getattr(model, field))

                self.session.add(existing_model)
                self.session.commit()
                return existing_model
            else:
                # Insert new model
                self.session.add(model)
                self.session.commit()
                return model
        except (IntegrityError, DataError) as e:
            # Handle specific database errors
            self.session.rollback()
            logger.error(f"Error upserting model: {e}")
            raise
        except ValueError as e:
            # Handle value errors related to invalid filter criteria
            self.session.rollback()
            logger.error(f"Value error during upsert: {e}")
            raise
        except Exception as e:
            # Handle unexpected errors
            self.session.rollback()
            logger.exception(f"Unexpected error upserting model: {e}")
            raise

    def get_model_by_id(
        self, model_class: Type[MedSearchBaseModel], model_id: int
    ) -> MedSearchBaseModel:
        """
        Retrieves a model instance by its ID.

        Queries the database for a model instance of the specified class
        with the given ID.

        Args:
            model_class (Type[MedSearchBaseModel]): The SQLAlchemy model class.
            model_id (int): The ID of the model instance to retrieve.

        Returns:
            Optional[MedSearchBaseModel]: The model instance if found,
            otherwise None.
        """

        return model_class.query.get(model_id)

    def get_model(
        self,
        model_class: Type[MedSearchBaseModel],
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Optional[MedSearchBaseModel]:
        """
        Retrieves a single model instance based on provided filters.

        Queries the database for a model instance of the specified class
        that matches the provided filter criteria. Optionally applies a
        limit and offset for pagination.

        Args:
            model_class (Type[MedSearchBaseModel]): The SQLAlchemy model class.
            filters (Optional[Dict[str, Any]]): Key-value pairs representing
            the filter criteria (optional).
            limit (Optional[int]): Maximum number of results to return (optional).
            offset (Optional[int]): Offset for pagination (optional).

        Returns:
            Optional[MedSearchBaseModel]: The model instance if found,
            otherwise None.
        """

        return self.session.query(model_class).filter_by(**filters).first()

    def get_models(
        self,
        model_class: Type[MedSearchBaseModel],
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[MedSearchBaseModel]:
        """
        Retrieves a list of model instances based on provided filters.

        Queries the database for model instances of the specified class
        that match the provided filter criteria. Optionally applies a
        limit and offset for pagination.

        Args:
            model_class (Type[MedSearchBaseModel]): The SQLAlchemy model class.
            filters (Optional[Dict[str, Any]]): Key-value pairs representing
            the filter criteria (optional).
            limit (Optional[int]): Maximum number of results to return (optional).
            offset (Optional[int]): Offset for pagination (optional).

        Returns:
            List[MedSearchBaseModel]: A list of model instances matching
            the filters.
        """

        query = self.session.query(model_class)
        if filters:
            query = query.filter_by(**filters)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        return query.all()
