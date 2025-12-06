"""
SQLAlchemy implementation of TableRepository.

Provides database persistence for cafe tables.
"""

# Import typing for type hints
from typing import List, Optional

# Import Session for database operations
from sqlalchemy.orm import Session

# Import domain entity and repository interface
from domain.entities.table import Table
from domain.repositories.table_repository import TableRepository

# Import SQLAlchemy model
from infrastructure.persistence.sqlalchemy_models import TableModel


class SQLAlchemyTableRepository(TableRepository):
    """
    Database-backed implementation of TableRepository.

    Manages cafe tables in the database.
    Translates between TableModel (database) and Table (domain).
    """

    def __init__(self, session: Session):
        """
        Initialize repository with database session.

        Args:
            session: SQLAlchemy Session for database operations
        """
        # Store session for all database operations
        self._session = session

    def list_all_tables(self) -> List[Table]:
        """
        Get all tables from database.

        Returns:
            List[Table]: All tables as domain entities
        """
        # Query database for all table rows
        # .query(TableModel) = SELECT * FROM tables
        # .all() executes query and returns list
        db_tables = self._session.query(TableModel).all()

        # Convert each database model to domain entity
        return [self._model_to_entity(table) for table in db_tables]

    def get_table_by_id(self, table_id: str) -> Optional[Table]:
        """
        Find table by ID.

        Args:
            table_id: Unique identifier for table

        Returns:
            Table if found, None if not found
        """
        # Query for table with matching ID
        # .filter() adds WHERE clause: WHERE id = table_id
        # .first() returns first result or None if no matches
        db_table = self._session.query(TableModel).filter(
            TableModel.id == table_id
        ).first()

        # Return None if table not found
        if db_table is None:
            return None

        # Convert model to entity and return
        return self._model_to_entity(db_table)

    def _model_to_entity(self, model: TableModel) -> Table:
        """
        Convert database model to domain entity.

        Args:
            model: TableModel from database

        Returns:
            Table: Domain entity
        """
        # Map database fields to entity fields
        # All fields have same names, simple one-to-one mapping
        return Table(
            id=model.id,  # Table ID
            number=model.number,  # Table number (display)
            capacity=model.capacity,  # Max people
            location=model.location  # Physical location
        )
