# Import type hints for better code clarity
from typing import Optional

# Import domain entities
# These are the core business objects from the domain layer
from domain.entities.menu import MenuItem

# Import repository interface (port)
# This is an abstract interface - we don't know if it's in-memory or database
from domain.repositories.menu_repository import MenuRepository


"""
GetMenuItem Use Case

MODULE 4 NEW USE CASE - Retrieve a single menu item by its ID.

PURPOSE:
- Get detailed information about a specific menu item
- Used by API endpoint GET /menu/items/{item_id}
- Simple delegation to repository (no complex logic needed)

RESPONSIBILITIES:
- Validate that item_id is provided
- Delegate to repository to fetch item
- Return item or None if not found

WHY THIS IS A USE CASE:
Even though this is simple (just calls repository), making it a use case:
1. Keeps consistent architecture (all business operations are use cases)
2. Allows adding logic later (e.g., logging, caching, permissions)
3. Makes testing easier (can mock the use case in route tests)
4. Documents business intent ("get menu item" vs "repository.get_item_by_id")

CLEAN ARCHITECTURE:
- Application layer (this file)
- Depends only on domain layer (MenuItem, MenuRepository)
- No knowledge of HTTP, database, or infrastructure
- Can be tested without FastAPI or database
"""


class GetMenuItem:
    """
    Use case for retrieving a single menu item by ID.

    This is a READ operation that retrieves one entity from the repository.

    Attributes:
        _menu_repository: Repository for accessing menu item data
    """

    def __init__(self, menu_repository: MenuRepository):
        """
        Initialize the use case with required repository.

        Args:
            menu_repository: Implementation of MenuRepository interface
                            Could be in-memory, database, or any implementation

        DEPENDENCY INJECTION:
        The repository is injected, not created here.
        This means:
        - Use case doesn't know if repository uses database or memory
        - Easy to swap implementations (for testing or changing storage)
        - Follows Dependency Inversion Principle (depend on abstraction)
        """
        # Store repository for later use
        # Prefix with underscore to indicate it's private (internal to class)
        self._menu_repository = menu_repository

    def execute(self, item_id: str) -> Optional[MenuItem]:
        """
        Execute the use case: get menu item by ID.

        Args:
            item_id: Unique identifier of the menu item to retrieve

        Returns:
            MenuItem if found, None if not found

        SIMPLE DELEGATION:
        This use case is simple - it just delegates to the repository.
        No complex business logic here.

        In the future, we might add:
        - Logging: log every time an item is accessed
        - Caching: cache frequently accessed items
        - Authorization: check if user can view this item
        - Analytics: track which items are viewed most
        - Related data: also fetch related items or reviews

        Example:
            # In a route or test:
            use_case = GetMenuItem(menu_repository)
            item = use_case.execute(item_id="item-001")
            if item is None:
                # Item not found, return 404
                pass
            else:
                # Item found, return it
                pass
        """

        # Delegate to repository to fetch the item
        # Repository knows HOW to get the item (from database, memory, etc.)
        # Use case knows WHEN and WHY to get the item (business logic)
        item = self._menu_repository.get_item_by_id(item_id)

        # Return the item (or None if not found)
        # Caller is responsible for handling None case
        return item

    # Note: We could add validation here if needed
    # For example:
    # if not item_id or not item_id.strip():
    #     raise ValueError("item_id cannot be empty")
    #
    # But for now, we keep it simple and let FastAPI handle validation
