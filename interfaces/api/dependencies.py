# Import the concrete repository implementation
# Infrastructure layer - this is where we decide which adapter to use
from infrastructure.persistence.in_memory_menu_repository import InMemoryMenuRepository

# Import the use case from application layer
from application.use_cases.list_menu_items import ListMenuItems


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


# Module-level singleton repository
# This creates ONE instance that's reused across all requests
# It's a simple approach for now - later we might use a DI container
# Note: Module-level variables are created once when Python imports the module
_menu_repository = InMemoryMenuRepository()

# Why a singleton here?
# - For in-memory repository, we want to share the same data across requests
# - If we created a new one each time, each request would see an empty menu!
# - Later with a database, we'd use connection pooling instead


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


# Future: We might add more dependency functions
# def get_create_menu_item_use_case():
#     repository = get_menu_repository()
#     return CreateMenuItem(menu_repository=repository)
#
# def get_update_menu_item_use_case():
#     repository = get_menu_repository()
#     return UpdateMenuItem(menu_repository=repository)
#
# The pattern is the same: get dependencies, inject them, return use case
