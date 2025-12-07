# Import List for type hints
# List[MenuItem] means "a list containing MenuItem objects"
from typing import List

# Import the MenuItem domain entity
# Use cases work with domain entities
from domain.entities.menu import MenuItem

# Import the MenuRepository port (interface)
# Notice: we import the INTERFACE, not a concrete implementation
# This is the Dependency Inversion Principle in action
from domain.repositories.menu_repository import MenuRepository


class ListMenuItems:
    """
    Use case for listing menu items.

    WHAT IS A USE CASE?
    - A use case represents one business operation or user story
    - Examples: "list menu items", "place an order", "add item to cart"
    - Use cases coordinate between domain entities and repositories
    - They contain APPLICATION logic, not domain logic

    APPLICATION LOGIC vs DOMAIN LOGIC:
    - Domain logic: rules that are ALWAYS true (price can't be negative)
    - Application logic: how we orchestrate operations (get items, filter them, return them)

    WHY A SEPARATE CLASS?
    - Single Responsibility: this class does ONE thing
    - Testable: easy to test without FastAPI or database
    - Reusable: could be used from API, CLI, or background job
    - Framework-agnostic: no FastAPI dependencies here

    DEPENDENCY INJECTION:
    - We receive the repository in the constructor
    - We DON'T create it ourselves (no "self.repo = InMemoryMenuRepository()")
    - This makes testing easy - pass in a fake repository
    - This makes swapping implementations easy - just pass a different repository
    """

    def __init__(self, menu_repository: MenuRepository):
        """
        Initialize the use case with its dependencies.

        Args:
            menu_repository (MenuRepository): The repository to fetch menu items from
                Notice the type hint is the INTERFACE, not a concrete class
                This means any class that implements MenuRepository will work

        Why constructor injection?
        - Clear dependencies: you can see what this class needs
        - Testability: easy to pass mocks/fakes in tests
        - Flexibility: can change implementation without changing this code
        """
        # Store the repository for later use
        # Convention: private attribute starts with underscore
        # This means "don't access this from outside the class"
        self._menu_repository = menu_repository

    def execute(
        self,
        only_available: bool = True,
        category_id: str | None = None,  # MODULE 4: Filter by category
        search: str | None = None,  # MODULE 4: Search by name/description
        limit: int = 20,  # MODULE 4: Pagination - max items to return
        offset: int = 0  # MODULE 4: Pagination - items to skip
    ) -> List[MenuItem]:
        """
        Execute the use case: list menu items with optional filtering, searching, and pagination.

        MODULE 4 ENHANCEMENTS:
        - Added category_id filter
        - Added search functionality
        - Added pagination support (limit/offset)
        - Delegate filtering to repository layer (more efficient than filtering in memory)

        Args:
            only_available (bool): If True, return only available items. Default: True.
            category_id (str | None): Filter by category ID. None means all categories.
            search (str | None): Search text for name/description. None means no search filter.
            limit (int): Maximum number of items to return. Default: 20.
            offset (int): Number of items to skip (for pagination). Default: 0.

        Returns:
            List[MenuItem]: List of menu items matching filters (may be empty)

        WHY DELEGATE TO REPOSITORY?
        In Module 3, we fetched ALL items then filtered in memory.
        In Module 4, we pass filters to repository so database can filter efficiently.

        Benefits of database filtering:
        - Faster: database only returns matching items (not all 10,000)
        - Less memory: don't load all items into Python
        - Database indexes: optimized for searching/filtering
        - Pagination: only fetch items needed for current page

        Example:
            # Get second page of available coffee items matching "espresso"
            use_case = ListMenuItems(menu_repository)
            items = use_case.execute(
                only_available=True,
                category_id="cat-001",
                search="espresso",
                limit=20,
                offset=20  # Skip first 20 items (page 1)
            )
        """

        # MODULE 4: Delegate filtering to repository layer
        # The repository will build an efficient database query
        # Instead of fetching everything and filtering in Python
        items = self._menu_repository.list_items(
            only_available=only_available,
            category_id=category_id,
            search=search,
            limit=limit,
            offset=offset
        )

        # Return the items
        # Repository already applied all filters and pagination
        return items

        # Note: We moved filtering logic from use case to repository
        # Old way (Module 3): fetch all, filter in Python
        # New way (Module 4): let database do the filtering
        # This is more efficient for large datasets!
