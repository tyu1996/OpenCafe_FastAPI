# Import the concrete repository implementations
# Infrastructure layer - this is where we decide which adapters to use
from infrastructure.persistence.in_memory_menu_repository import InMemoryMenuRepository
from infrastructure.persistence.in_memory_category_repository import InMemoryCategoryRepository
from infrastructure.persistence.in_memory_table_repository import InMemoryTableRepository
from infrastructure.persistence.in_memory_order_repository import InMemoryOrderRepository

# Import use cases from application layer
from application.use_cases.list_menu_items import ListMenuItems
from application.use_cases.list_menu_categories import ListMenuCategories
from application.use_cases.get_table import GetTable
from application.use_cases.place_order import PlaceOrder


"""
Dependency Injection Configuration for FastAPI

WHAT IS DEPENDENCY INJECTION (DI)?
- A design pattern where objects receive their dependencies from outside
- Instead of creating dependencies inside, we "inject" them from outside
- Example: use_case = ListMenuItems(repository) <- repository is injected

WHY USE DI?
- Flexibility: easy to swap implementations (in-memory -> database)
- Testability: easy to inject fakes/mocks in tests
- Separation of concerns: objects don't know how to create their dependencies
- Single Responsibility: each class does one thing

FASTAPI'S DI SYSTEM:
- FastAPI has built-in DI using the Depends() function
- Functions that provide dependencies are called "dependency functions"
- FastAPI calls these functions automatically and passes results to route handlers

This file is the "composition root" - where we wire up our dependencies.
"""


# Module-level singleton repositories
# These create ONE instance of each repository that's reused across all requests
# This is a simple approach for in-memory repositories
# Note: Module-level variables are created once when Python imports the module
_menu_repository = InMemoryMenuRepository()
_category_repository = InMemoryCategoryRepository()
_table_repository = InMemoryTableRepository()
_order_repository = InMemoryOrderRepository()

# Why singletons here?
# - For in-memory repositories, we want to share the same data across requests
# - If we created new instances each time, each request would see empty data!
# - This simulates a shared database that persists across requests
# - Later with a real database, we'd use connection pooling instead


def get_menu_repository():
    """
    Dependency function that provides the MenuRepository.

    Returns:
        MenuRepository: The repository instance to use for data access

    HOW FASTAPI USES THIS:
    When you use Depends(get_menu_repository) in a route parameter,
    FastAPI automatically calls this function and injects the result.

    Example:
        @router.get("/items")
        def list_items(repo = Depends(get_menu_repository)):
            # FastAPI calls get_menu_repository() and passes result as 'repo'
            items = repo.list_all_items()
            return items

    WHY A FUNCTION?
    - FastAPI's DI system expects functions
    - Functions can do setup/teardown (like opening/closing database connections)
    - Functions can check request context (like auth tokens)
    - For now, we just return the singleton, but we have flexibility for later
    """
    # Return the singleton repository instance
    return _menu_repository

    # In a more complex system, this might:
    # - Check if user is authenticated
    # - Create a database session
    # - Do request-specific setup
    # - Log the access
    # But for now, simple is good!


def get_list_menu_items_use_case():
    """
    Dependency function that provides the ListMenuItems use case.

    Returns:
        ListMenuItems: An instance of the use case, with repository already injected

    This is a FACTORY FUNCTION - it creates and configures the use case.

    HOW THIS WORKS:
    1. We call get_menu_repository() to get the repository
    2. We create a ListMenuItems instance and inject the repository
    3. We return the configured use case
    4. FastAPI injects this into our route handlers

    Example usage in a route:
        @router.get("/items")
        def list_items(use_case = Depends(get_list_menu_items_use_case)):
            # FastAPI gives us a fully configured use case
            # The use case already has its repository dependency
            items = use_case.execute()
            return items

    WHY THIS PATTERN?
    - Composition: we compose the use case from its dependencies
    - Testability: in tests, we can provide a different function
    - Single place: all wiring happens here, not scattered in routes
    - Type safety: return type tells you exactly what you get
    """

    # Step 1: Get the repository dependency
    # We could also use Depends() here for more complex scenarios
    repository = get_menu_repository()

    # Step 2: Create the use case with its dependency injected
    # This is manual dependency injection - we construct the object graph
    use_case = ListMenuItems(menu_repository=repository)

    # Step 3: Return the configured use case
    return use_case

    # Alternative (more advanced) approach:
    # In larger apps, you might use a DI container like:
    # - dependency_injector
    # - punq
    # - injector
    # These automate the wiring, but add complexity
    # For our size, manual wiring is clearer


# ===== Category Dependencies =====

def get_category_repository():
    """
    Dependency function that provides the CategoryRepository.

    Returns the singleton in-memory repository.
    """
    return _category_repository


def get_list_menu_categories_use_case():
    """
    Dependency function that provides the ListMenuCategories use case.

    Returns:
        ListMenuCategories: Use case with repository already injected

    Pattern: Get repository → Create use case → Return configured use case
    """
    repository = get_category_repository()
    use_case = ListMenuCategories(category_repository=repository)
    return use_case


# ===== Table Dependencies =====

def get_table_repository():
    """
    Dependency function that provides the TableRepository.

    Returns the singleton in-memory repository.
    """
    return _table_repository


def get_get_table_use_case():
    """
    Dependency function that provides the GetTable use case.

    Returns:
        GetTable: Use case with repository already injected
    """
    repository = get_table_repository()
    use_case = GetTable(table_repository=repository)
    return use_case


# ===== Order Dependencies =====

def get_order_repository():
    """
    Dependency function that provides the OrderRepository.

    Returns the singleton in-memory repository.
    This repository stores orders created during this server session.
    """
    return _order_repository


def get_place_order_use_case():
    """
    Dependency function that provides the PlaceOrder use case.

    This is more complex than other use cases because it has 3 dependencies:
    - OrderRepository: to save the new order
    - TableRepository: to validate table exists
    - MenuRepository: to look up item details and prices

    Returns:
        PlaceOrder: Use case with all 3 repositories injected

    This demonstrates multi-repository coordination!
    """
    # Get all three repository dependencies
    order_repo = get_order_repository()
    table_repo = get_table_repository()
    menu_repo = get_menu_repository()

    # Create use case with all dependencies injected
    # PlaceOrder needs all three repositories to do its job
    use_case = PlaceOrder(
        order_repository=order_repo,
        table_repository=table_repo,
        menu_repository=menu_repo,
    )

    return use_case


# ===== Summary =====
# This file now provides dependency functions for:
# - 4 repositories (menu, category, table, order)
# - 4 use cases (list items, list categories, get table, place order)
#
# Pattern is consistent:
# 1. Create singleton repositories at module level
# 2. Provide get_X_repository() functions
# 3. Provide get_X_use_case() functions that wire up dependencies
#
# In Module 3, when we switch to SQLAlchemy:
# - We'll replace InMemory* with SQLAlchemy* implementations
# - The dependency functions stay the same!
# - Use cases don't change at all!
# That's the power of dependency injection!
