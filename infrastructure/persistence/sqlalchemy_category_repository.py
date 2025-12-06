"""
SQLAlchemy implementation of CategoryRepository.

Provides database persistence for menu categories.
"""

# Import typing for type hints
from typing import List, Optional

# Import Session for database operations
from sqlalchemy.orm import Session

# Import domain entity and repository interface
from domain.entities.category import MenuCategory
from domain.repositories.category_repository import CategoryRepository

# Import SQLAlchemy model
from infrastructure.persistence.sqlalchemy_models import MenuCategoryModel


class SQLAlchemyCategoryRepository(CategoryRepository):
    """
    Database-backed implementation of CategoryRepository.

    Manages menu categories in the database.
    Translates between MenuCategoryModel (database) and MenuCategory (domain).
    """

    def __init__(self, session: Session):
        """
        Initialize repository with database session.

        Args:
            session: SQLAlchemy Session for database operations
        """
        # Store session for use in all methods
        self._session = session

    def list_all_categories(self) -> List[MenuCategory]:
        """
        Get all categories from database.

        Returns:
            List[MenuCategory]: All categories as domain entities
        """
        # Query database for all category rows
        # .query(MenuCategoryModel) = SELECT * FROM menu_categories
        # .all() executes and returns list of model objects
        db_categories = self._session.query(MenuCategoryModel).all()

        # Convert each database model to domain entity
        # Using list comprehension for clean, concise code
        return [self._model_to_entity(cat) for cat in db_categories]

    def get_category_by_id(self, category_id: str) -> Optional[MenuCategory]:
        """
        Find category by ID.

        Args:
            category_id: Unique identifier for category

        Returns:
            MenuCategory if found, None if not found
        """
        # Query for category with matching ID
        # .filter() adds WHERE clause
        # .first() returns first result or None
        db_category = self._session.query(MenuCategoryModel).filter(
            MenuCategoryModel.id == category_id
        ).first()

        # Return None if not found
        if db_category is None:
            return None

        # Convert model to entity
        return self._model_to_entity(db_category)

    def _model_to_entity(self, model: MenuCategoryModel) -> MenuCategory:
        """
        Convert database model to domain entity.

        Args:
            model: MenuCategoryModel from database

        Returns:
            MenuCategory: Domain entity
        """
        # Map database fields to entity fields
        # Simple one-to-one mapping for categories
        return MenuCategory(
            id=model.id,  # Category ID
            name=model.name,  # Category name
            description=model.description  # Category description
        )
