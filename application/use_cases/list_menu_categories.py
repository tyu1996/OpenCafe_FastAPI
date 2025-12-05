# Import List for type hints
from typing import List

# Import the domain entity this use case works with
from domain.entities.category import MenuCategory

# Import the repository interface (port)
# Notice: we depend on the INTERFACE, not a concrete implementation
from domain.repositories.category_repository import CategoryRepository


class ListMenuCategories:
    """
    Use case for listing all menu categories.

    WHAT IS A USE CASE?
    - Represents one business operation: "list menu categories"
    - Coordinates between domain entities and repositories
    - Contains APPLICATION logic, not domain logic
    - Framework-agnostic: no FastAPI, no HTTP, just pure Python

    WHY THIS USE CASE?
    - Customers need to browse menu by category
    - Shows menu structure (Coffee, Pastries, Sandwiches, etc.)
    - First step in menu browsing flow
    - Simpler than ListMenuItems (no filtering needed)

    Real-world analogy: Think of this like the table of contents in a menu book.
    Before seeing individual items, customers see the main sections.

    PATTERN:
    This follows the same pattern as ListMenuItems:
    1. Constructor receives dependencies (repository)
    2. execute() method performs the operation
    3. Returns domain entities (not DTOs)
    4. Router converts entities to DTOs

    DEPENDENCY INJECTION:
    - Repository is injected in constructor (not created inside)
    - Makes testing easy: pass fake repository
    - Makes swapping implementations easy: just pass different repository
    """

    def __init__(self, category_repository: CategoryRepository):
        """
        Initialize the use case with its dependencies.

        Args:
            category_repository (CategoryRepository): Repository for accessing categories
                Notice: type is the INTERFACE, not a concrete class
                Any class implementing CategoryRepository will work

        Why constructor injection?
        - Clear dependency declaration
        - Testable: easy to pass mocks/fakes
        - Flexible: swap implementations without code changes
        """
        # Store repository for later use
        # Convention: private attribute starts with underscore
        self._category_repository = category_repository

    def execute(self) -> List[MenuCategory]:
        """
        Execute the use case: list all menu categories.

        This is the main business operation.
        Method name 'execute' follows command pattern convention.

        NO PARAMETERS NEEDED:
        Unlike ListMenuItems (which has only_available parameter),
        this use case has no options. We always return ALL categories.

        Why no filtering?
        - Categories are relatively stable (don't change often)
        - All categories are relevant to show menu structure
        - No concept of "available" vs "unavailable" categories
        - If needed, filtering would happen at application layer

        Returns:
            List[MenuCategory]: All categories (may be empty if none defined)

        Algorithm:
        1. Get all categories from repository
        2. Return them as-is (no filtering or transformation)

        That's it! Very simple use case.
        """

        # Step 1: Get all categories from repository
        # Delegate data fetching to the repository (that's its job)
        # We don't know (or care) if they come from memory, database, or API
        categories = self._category_repository.list_all_categories()

        # Step 2: Return categories
        # No filtering, no sorting, no transformation
        # Just return what we got from the repository
        return categories

        # Note: This use case is intentionally simple
        # More complex use cases might:
        # - Filter categories based on availability
        # - Sort categories by display order
        # - Enrich with item counts per category
        # - Validate user permissions
        # But we keep this simple (KISS principle)

    # TESTING NOTE:
    # This use case is easy to test without FastAPI or database:
    #
    # def test_list_categories():
    #     # Create fake repository with test data
    #     fake_repo = FakeCategoryRepository([cat1, cat2, cat3])
    #
    #     # Create use case with fake
    #     use_case = ListMenuCategories(fake_repo)
    #
    #     # Execute
    #     result = use_case.execute()
    #
    #     # Verify
    #     assert len(result) == 3
    #     assert result[0].name == "Coffee Drinks"
