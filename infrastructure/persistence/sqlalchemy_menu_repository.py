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

# Import SQLAlchemy query functions for complex queries (MODULE 4)
from sqlalchemy import or_  # For OR conditions in queries

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

    def list_items(
        self,
        only_available: bool = True,
        category_id: str | None = None,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[MenuItem]:
        """
        List menu items with filtering, searching, and pagination.

        MODULE 4 NEW METHOD - Enhanced querying with database optimization.

        This method builds a SQL query dynamically based on filters.
        Database does the filtering, not Python (much more efficient!).

        Args:
            only_available: If True, filter to available items only
            category_id: If provided, filter to specific category
            search: If provided, search in name and description
            limit: Maximum items to return (pagination)
            offset: Items to skip (pagination)

        Returns:
            List[MenuItem]: Filtered menu items as domain entities

        SQL Example (when all filters applied):
            SELECT * FROM menu_items
            WHERE available = 1
              AND category_id = 'cat-001'
              AND (name LIKE '%espresso%' OR description LIKE '%espresso%')
            LIMIT 20 OFFSET 0
        """
        # Start building the query
        # This creates a SELECT query for MenuItemModel
        # No WHERE clause yet - we'll add filters below
        query = self._session.query(MenuItemModel)

        # FILTER 1: Availability (MODULE 4)
        # If only_available is True, filter to available=1 items
        if only_available:
            # Add WHERE clause: available = 1
            # Note: SQLite stores booleans as 0/1 integers
            query = query.filter(MenuItemModel.available == 1)

        # FILTER 2: Category (MODULE 4)
        # If category_id provided, filter to that category
        if category_id is not None:
            # Add WHERE clause: category_id = ?
            # This uses parameterized query (safe from SQL injection)
            query = query.filter(MenuItemModel.category_id == category_id)

        # FILTER 3: Search (MODULE 4)
        # If search text provided, search in name OR description
        if search is not None:
            # Create search pattern for LIKE query
            # %text% matches "text" anywhere in the string
            # Example: "%espresso%" matches "Double Espresso", "Espresso Shot"
            search_pattern = f"%{search}%"

            # Add WHERE clause with OR condition
            # Search in both name and description fields
            # ilike() is case-insensitive LIKE (espresso matches Espresso)
            query = query.filter(
                or_(  # OR condition (match either field)
                    MenuItemModel.name.ilike(search_pattern),  # Search in name
                    MenuItemModel.description.ilike(search_pattern)  # Search in description
                )
            )

        # PAGINATION (MODULE 4)
        # Apply limit and offset LAST (after all filters)
        # Limit: maximum number of items to return
        # Offset: number of items to skip (for page 2, 3, etc.)
        # Example: offset=20, limit=10 returns items 21-30
        query = query.limit(limit).offset(offset)

        # Execute the query
        # .all() runs the query and returns list of MenuItemModel objects
        # Database returns only the filtered, paginated results
        # Much more efficient than fetching all items and filtering in Python!
        db_items = query.all()

        # Convert database models to domain entities
        # List comprehension calls _model_to_entity for each item
        return [self._model_to_entity(item) for item in db_items]

        # Query building summary:
        # 1. Start with base query
        # 2. Add WHERE clauses for filters (if provided)
        # 3. Add LIMIT and OFFSET for pagination
        # 4. Execute query (database does the work!)
        # 5. Convert results to domain entities

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
