"""
SQLAlchemy implementation of MenuRepository.

This adapter bridges between domain entities (MenuItem) and database models (MenuItemModel).
It translates database operations into domain concepts.
"""

# Import typing utilities for type hints
from typing import List, Optional

# Import Decimal for precise money calculations
from decimal import Decimal

# Import Session from SQLAlchemy - manages database transactions
from sqlalchemy.orm import Session

# Import domain entity and repository interface
# Infrastructure knows about domain (dependency flows inward)
from domain.entities.menu import MenuItem
from domain.repositories.menu_repository import MenuRepository

# Import SQLAlchemy models (database layer)
from infrastructure.persistence.sqlalchemy_models import MenuItemModel


class SQLAlchemyMenuRepository(MenuRepository):
    """
    Database-backed implementation of MenuRepository using SQLAlchemy.

    This is an ADAPTER that implements the MenuRepository PORT.
    It provides the same interface as InMemoryMenuRepository but stores data in a database.

    WHAT IS A SESSION?
    - Session is like a "shopping cart" for database operations
    - You query and modify objects in the session
    - call session.commit() to save all changes at once
    - call session.rollback() to discard all changes
    - Sessions are created per-request via dependency injection

    Real-world analogy:
    - In-memory repository = whiteboard (erases when you turn off server)
    - Database repository = filing cabinet (persists permanently)
    - But to the application layer, both look identical (same interface)!
    """

    def __init__(self, session: Session):
        """
        Initialize repository with a database session.

        Args:
            session: SQLAlchemy Session for database operations
                     Provided by FastAPI dependency injection
                     Each request gets its own session
        """
        # Store session as instance variable
        # Used by all methods to query and modify database
        self._session = session

    def list_all_items(self) -> List[MenuItem]:
        """
        Retrieve all menu items from database.

        HOW IT WORKS:
        1. Query database for all MenuItemModel rows
        2. Convert each database model to MenuItem domain entity
        3. Return list of domain entities

        Returns:
            List[MenuItem]: All menu items as domain entities
        """
        # Query database for all menu items
        # session.query() creates a query object
        # .query(MenuItemModel) means "SELECT * FROM menu_items"
        # .all() executes query and returns list of MenuItemModel objects
        db_items = self._session.query(MenuItemModel).all()

        # Convert each database model to domain entity
        # List comprehension: [f(x) for x in list]
        # Calls _model_to_entity() for each item in db_items
        return [self._model_to_entity(item) for item in db_items]

    def get_item_by_id(self, item_id: str) -> Optional[MenuItem]:
        """
        Find a single menu item by ID from database.

        Args:
            item_id: Unique identifier for the menu item

        Returns:
            MenuItem if found, None if not found
        """
        # Query database for item with matching ID
        # .filter() adds WHERE clause
        # MenuItemModel.id == item_id becomes "WHERE id = ?"
        # .first() returns first match or None if no matches
        db_item = self._session.query(MenuItemModel).filter(
            MenuItemModel.id == item_id
        ).first()

        # If item not found in database, return None
        if db_item is None:
            return None

        # Convert database model to domain entity and return
        return self._model_to_entity(db_item)

    def _model_to_entity(self, model: MenuItemModel) -> MenuItem:
        """
        Convert SQLAlchemy model to domain entity.

        This is the TRANSLATION layer between infrastructure and domain.

        WHY SEPARATE MODELS AND ENTITIES?
        - Models = how data is stored (database structure, SQLAlchemy)
        - Entities = business concepts (domain logic, framework-free)
        - Separating them allows database changes without touching domain
        - Domain layer stays pure (no SQLAlchemy imports)

        Args:
            model: MenuItemModel from database

        Returns:
            MenuItem: Domain entity with same data

        Real-world analogy:
        - Model = raw ingredients in storage (database format)
        - Entity = prepared dish served to customer (domain format)
        - This method is the chef who transforms ingredients into dish
        """
        # Create MenuItem entity from model's data
        # Map database fields to entity fields
        # Convert boolean: SQLite stores as 0/1, convert to True/False
        return MenuItem(
            id=model.id,  # Copy ID as-is (both are strings)
            name=model.name,  # Copy name as-is
            description=model.description,  # Copy description as-is
            price=model.price,  # Already Decimal from database
            category=model.category_id,  # Map category_id to category field
            available=bool(model.available)  # Convert 0/1 to False/True
        )
