# Import database session management
# This is the new dependency for Module 3 - database sessions
from fastapi import Depends
from sqlalchemy.orm import Session
from infrastructure.persistence.database import get_db_session

# Import the SQLAlchemy repository implementations (NEW in Module 3)
# We're switching from in-memory to database-backed repositories
from infrastructure.persistence.sqlalchemy_menu_repository import SQLAlchemyMenuRepository
from infrastructure.persistence.sqlalchemy_category_repository import SQLAlchemyCategoryRepository
from infrastructure.persistence.sqlalchemy_table_repository import SQLAlchemyTableRepository
from infrastructure.persistence.sqlalchemy_order_repository import SQLAlchemyOrderRepository

# Note: In-memory repositories are used in unit tests (tests/unit/)
# They're imported there directly, not from this file

# Import use cases from application layer
# NOTE: Use cases don't change! Same code works with both in-memory and database repos
# This is the power of the repository pattern and dependency injection
from application.use_cases.list_menu_items import ListMenuItems
from application.use_cases.get_menu_item import GetMenuItem  # MODULE 4: New use case
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


# ===== MODULE 3 CHANGE: Database-backed repositories =====
# We NO LONGER use module-level singletons.
# Instead, each request gets its own database session via FastAPI's DI.
# Sessions are created per-request and closed automatically after response.

# Why per-request sessions?
# - Isolation: each request has independent transaction
# - Thread safety: no shared state between concurrent requests
# - Automatic cleanup: sessions close even if exception occurs
# - Connection pooling: SQLAlchemy reuses connections efficiently


def get_menu_repository(db: Session = Depends(get_db_session)):
    """
    Dependency function that provides the MenuRepository (DATABASE VERSION).

    MODULE 3 CHANGE:
    - Now accepts a database session as a dependency
    - Creates SQLAlchemyMenuRepository with that session
    - Each request gets fresh repository with its own session

    Args:
        db: Database session injected by FastAPI
            FastAPI calls get_db_session() and passes result here

    Returns:
        MenuRepository: Database-backed repository instance

    HOW THIS WORKS:
    1. FastAPI sees db: Session = Depends(get_db_session)
    2. FastAPI calls get_db_session() to create a session
    3. FastAPI passes that session to this function as 'db'
    4. We create SQLAlchemyMenuRepository with that session
    5. We return the repository to the route handler
    6. After route finishes, FastAPI closes the session (via yield in get_db_session)

    Example:
        @router.get("/items")
        def list_items(repo = Depends(get_menu_repository)):
            # repo is SQLAlchemyMenuRepository with a fresh session
            items = repo.list_all_items()
            return items
            # Session automatically closes after return

    POWER OF ABSTRACTION:
    - Use cases don't know this changed!
    - Routes don't know this changed!
    - Only this file changed - everything else is the same
    - Could switch back to in-memory by changing one line here
    """
    # Create database-backed repository with the session
    # This replaces: return _menu_repository (old in-memory version)
    return SQLAlchemyMenuRepository(session=db)


def get_list_menu_items_use_case(
    menu_repo = Depends(get_menu_repository)
):
    """
    Dependency function that provides the ListMenuItems use case.

    MODULE 3 CHANGE:
    - Now uses Depends() to inject menu repository
    - FastAPI handles the dependency chain automatically

    Args:
        menu_repo: Injected by FastAPI via Depends(get_menu_repository)

    Returns:
        ListMenuItems: An instance of the use case, with repository already injected

    This is a FACTORY FUNCTION - it creates and configures the use case.

    HOW THIS WORKS (Module 3 version):
    1. FastAPI sees menu_repo = Depends(get_menu_repository)
    2. FastAPI calls get_menu_repository() which needs a Session
    3. FastAPI calls get_db_session() to create a Session
    4. FastAPI passes Session to get_menu_repository()
    5. get_menu_repository() returns SQLAlchemyMenuRepository
    6. FastAPI passes that repository to this function as menu_repo
    7. We create ListMenuItems with that repository
    8. We return the configured use case

    Example usage in a route:
        @router.get("/items")
        def list_items(use_case = Depends(get_list_menu_items_use_case)):
            # FastAPI gives us a fully configured use case
            # The use case already has its repository dependency
            # The repository already has its session dependency
            items = use_case.execute()
            return items
    """

    # Create the use case with the injected repository
    # FastAPI already gave us the repository via Depends()
    use_case = ListMenuItems(menu_repository=menu_repo)

    # Return the configured use case
    return use_case


def get_get_menu_item_use_case(
    menu_repo = Depends(get_menu_repository)
):
    """
    Dependency function that provides the GetMenuItem use case.

    MODULE 4 NEW DEPENDENCY - For retrieving single menu item by ID.

    Args:
        menu_repo: Injected by FastAPI via Depends(get_menu_repository)

    Returns:
        GetMenuItem: Use case instance with repository injected

    Example usage in a route:
        @router.get("/items/{item_id}")
        def get_item(
            item_id: str,
            use_case = Depends(get_get_menu_item_use_case)
        ):
            item = use_case.execute(item_id=item_id)
            if item is None:
                raise HTTPException(404, detail="Not found")
            return item
    """
    # Create and return the use case with injected repository
    # Same pattern as other use case dependencies
    use_case = GetMenuItem(menu_repository=menu_repo)
    return use_case


# ===== Category Dependencies =====

def get_category_repository(db: Session = Depends(get_db_session)):
    """
    Dependency function that provides the CategoryRepository (DATABASE VERSION).

    Args:
        db: Database session injected by FastAPI

    Returns:
        CategoryRepository: Database-backed repository instance
    """
    # Create database-backed repository with session
    return SQLAlchemyCategoryRepository(session=db)


def get_list_menu_categories_use_case(
    category_repo = Depends(get_category_repository)
):
    """
    Dependency function that provides the ListMenuCategories use case.

    Args:
        category_repo: Injected by FastAPI via Depends(get_category_repository)

    Returns:
        ListMenuCategories: Use case with repository already injected
    """
    use_case = ListMenuCategories(category_repository=category_repo)
    return use_case


# ===== Table Dependencies =====

def get_table_repository(db: Session = Depends(get_db_session)):
    """
    Dependency function that provides the TableRepository (DATABASE VERSION).

    Args:
        db: Database session injected by FastAPI

    Returns:
        TableRepository: Database-backed repository instance
    """
    # Create database-backed repository with session
    return SQLAlchemyTableRepository(session=db)


def get_get_table_use_case(
    table_repo = Depends(get_table_repository)
):
    """
    Dependency function that provides the GetTable use case.

    Args:
        table_repo: Injected by FastAPI via Depends(get_table_repository)

    Returns:
        GetTable: Use case with repository already injected
    """
    use_case = GetTable(table_repository=table_repo)
    return use_case


# ===== Order Dependencies =====

def get_order_repository(db: Session = Depends(get_db_session)):
    """
    Dependency function that provides the OrderRepository (DATABASE VERSION).

    Args:
        db: Database session injected by FastAPI

    Returns:
        OrderRepository: Database-backed repository instance
    """
    # Create database-backed repository with session
    return SQLAlchemyOrderRepository(session=db)


def get_place_order_use_case(
    order_repo = Depends(get_order_repository),
    table_repo = Depends(get_table_repository),
    menu_repo = Depends(get_menu_repository)
):
    """
    Dependency function that provides the PlaceOrder use case.

    This is more complex than other use cases because it has 3 dependencies:
    - OrderRepository: to save the new order
    - TableRepository: to validate table exists
    - MenuRepository: to look up item details and prices

    MODULE 3 CHANGE:
    - All three repositories now use Depends() for injection
    - FastAPI manages the entire dependency graph automatically
    - All repositories in a single request share the same database session (FastAPI caches dependencies per request)

    Args:
        order_repo: Injected by FastAPI via Depends(get_order_repository)
        table_repo: Injected by FastAPI via Depends(get_table_repository)
        menu_repo: Injected by FastAPI via Depends(get_menu_repository)

    Returns:
        PlaceOrder: Use case with all 3 repositories injected

    This demonstrates multi-repository coordination with database persistence!
    """
    # Create use case with all dependencies injected
    # FastAPI already gave us all three repositories via Depends()
    # PlaceOrder needs all three repositories to do its job
    use_case = PlaceOrder(
        order_repository=order_repo,
        table_repository=table_repo,
        menu_repository=menu_repo,
    )

    return use_case


# ===== Summary (Updated for Module 3) =====
# This file now provides dependency functions for:
# - 4 repositories (menu, category, table, order) - NOW DATABASE-BACKED!
# - 4 use cases (list items, list categories, get table, place order) - UNCHANGED!
#
# Pattern (Module 3 version):
# 1. Import SQLAlchemy repository implementations
# 2. get_X_repository(db: Session = Depends(get_db_session)) - create repo with session
# 3. get_X_use_case() - same as before, wire up dependencies
#
# What changed in Module 3?
# - Repository dependency functions now accept database session
# - They create SQLAlchemy* repos instead of InMemory* repos
# - Use cases stay EXACTLY the same!
# - Routes stay EXACTLY the same!
# - Domain layer stays EXACTLY the same!
#
# Only this file changed - that's the power of clean architecture!
