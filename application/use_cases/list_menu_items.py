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

    def execute(self, only_available: bool = True) -> List[MenuItem]:
        """
        Execute the use case: list menu items.

        This is where the actual business operation happens.
        Method is called 'execute' by convention (like Command pattern).

        Args:
            only_available (bool): If True, return only available items.
                                   If False, return ALL items including unavailable.
                                   Defaults to True because most customers only want to see available items.

        Returns:
            List[MenuItem]: List of menu items (may be empty if no items exist)

        Why 'only_available' parameter?
        - Gives flexibility: customers see available, staff might see everything
        - This is application logic (not domain) - it's about filtering for different views
        - Business rule: "customers should only see available items" lives here
        """

        # Step 1: Get ALL items from the repository
        # We delegate data fetching to the repository - that's its job
        # We don't know (or care) if items come from memory, database, or API
        items = self._menu_repository.list_all_items()

        # Step 2: Apply filtering based on availability
        # This is APPLICATION LOGIC: deciding which items to return
        if only_available:
            # List comprehension: keep only items where item.available is True
            # [item for item in items if condition] is Python's filter syntax
            items = [item for item in items if item.available]
            # This is equivalent to:
            # filtered_items = []
            # for item in items:
            #     if item.available:
            #         filtered_items.append(item)
            # items = filtered_items

        # Step 3: Return the filtered list
        # The caller (usually a router) will convert this to the appropriate response format
        return items

        # Note: More complex use cases might:
        # - Validate inputs
        # - Coordinate multiple repositories
        # - Emit domain events
        # - Handle transactions
        # But we keep this simple for now (KISS principle)
