# Import pytest for test fixtures
import pytest

# Import Decimal for test data
from decimal import Decimal

# Import FastAPI TestClient for integration testing
# TestClient lets us make HTTP requests to our API without running a server
from fastapi.testclient import TestClient

# Import SQLAlchemy components for test database
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker, Session

# Import our main FastAPI application
from main import app

# Import database dependencies for overriding
from infrastructure.persistence.database import get_db_session

# Import SQLAlchemy models and Base for table creation
from infrastructure.persistence.sqlalchemy_models import (
    Base,
    MenuCategoryModel,
    MenuItemModel,
    TableModel,
)


"""
Pytest Configuration and Shared Test Fixtures

WHAT IS conftest.py?
- Special file that pytest automatically loads
- Contains fixtures that are shared across multiple test files
- Fixtures are reusable test setup code
- Available to all tests in this directory and subdirectories

WHAT IS A FIXTURE?
- Function decorated with @pytest.fixture
- Provides test data or test resources
- Automatically passed to tests that request it
- Can do setup before test and cleanup after test

WHY USE FIXTURES?
- DRY (Don't Repeat Yourself): write setup code once, reuse everywhere
- Clean tests: tests focus on what they're testing, not setup
- Automatic cleanup: fixtures handle teardown automatically
- Type hints: IDE knows what type the fixture provides

MODULE 3 UPDATE:
- Added test database fixture using in-memory SQLite
- Tests now run against isolated database (not production opencafe.db)
- Each test session gets fresh database with seeded test data
- Dependencies are overridden to use test database
"""

# ===== TEST DATABASE SETUP =====
# Use in-memory SQLite for tests (fast, isolated, no cleanup needed)
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine with StaticPool to share in-memory database across connections
# Without StaticPool, each connection gets a new in-memory database!
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite with FastAPI
    poolclass=StaticPool,  # Ensures all connections share the same in-memory database
)

# Create test session factory
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


def override_get_db_session():
    """
    Override dependency to use test database instead of production.
    
    This replaces the production get_db_session() with one that
    connects to our in-memory test database.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_test_database(db: Session):
    """
    Seed test database with sample data.
    
    Creates consistent test data that tests can rely on.
    Similar to seed_data.py but for testing.
    """
    # Create categories
    coffee = MenuCategoryModel(
        id="cat-001",
        name="Coffee Drinks",
        description="Hot and cold coffee beverages"
    )
    pastries = MenuCategoryModel(
        id="cat-002",
        name="Pastries",
        description="Fresh baked goods"
    )
    db.add(coffee)
    db.add(pastries)
    
    # Create menu items (6 total, 1 unavailable - matches test expectations)
    items = [
        MenuItemModel(
            id="item-001", name="Espresso", description="Strong Italian coffee",
            price=Decimal("2.50"), category_id="cat-001", available=1
        ),
        MenuItemModel(
            id="item-002", name="Cappuccino", description="Espresso with steamed milk",
            price=Decimal("3.50"), category_id="cat-001", available=1
        ),
        MenuItemModel(
            id="item-003", name="Croissant", description="Buttery French pastry",
            price=Decimal("3.00"), category_id="cat-002", available=1
        ),
        MenuItemModel(
            id="item-004", name="Blueberry Muffin", description="Fresh baked muffin",
            price=Decimal("2.75"), category_id="cat-002", available=1
        ),
        MenuItemModel(
            id="item-005", name="Latte", description="Espresso with lots of milk",
            price=Decimal("4.00"), category_id="cat-001", available=1
        ),
        MenuItemModel(
            id="item-006", name="Seasonal Special", description="Limited time offer",
            price=Decimal("5.00"), category_id="cat-001", available=0  # UNAVAILABLE
        ),
    ]
    for item in items:
        db.add(item)
    
    # Create tables
    tables = [
        TableModel(id="table-001", number=1, capacity=2, location="window"),
        TableModel(id="table-002", number=2, capacity=4, location="main-room"),
        TableModel(id="table-003", number=3, capacity=4, location="patio"),
        TableModel(id="table-004", number=4, capacity=6, location="main-room"),
    ]
    for table in tables:
        db.add(table)
    
    db.commit()


@pytest.fixture(scope="session")
def setup_test_database():
    """
    Session-scoped fixture to create and seed test database once.
    
    Scope="session" means this runs once per test session, not per test.
    All tests share the same database (but each gets its own session).
    """
    # Create all tables in test database
    Base.metadata.create_all(bind=test_engine)
    
    # Seed with test data
    db = TestingSessionLocal()
    try:
        seed_test_database(db)
    finally:
        db.close()
    
    yield  # Tests run here
    
    # Cleanup: drop all tables after tests complete
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(setup_test_database):
    """
    Fixture that provides a FastAPI TestClient with test database.

    Returns:
        TestClient: Client for making HTTP requests to the API

    MODULE 3 UPDATE:
    - Now depends on setup_test_database fixture
    - Overrides get_db_session to use test database
    - Tests run against isolated in-memory SQLite
    - No interference with production opencafe.db

    WHAT IS TestClient?
    - Simulates a web browser or API client
    - Makes real HTTP requests to your FastAPI app
    - But doesn't require running a server
    - Synchronous (no async/await needed in tests)
    - Based on httpx library

    HOW TO USE IN TESTS:
        def test_something(client):  # Request 'client' fixture
            response = client.get("/some/endpoint")
            assert response.status_code == 200
    """
    # Override the database dependency to use test database
    app.dependency_overrides[get_db_session] = override_get_db_session
    
    # Create a TestClient wrapping our FastAPI app
    with TestClient(app) as test_client:
        yield test_client
    
    # Cleanup: remove the override after tests
    app.dependency_overrides.clear()


@pytest.fixture
def db_session(setup_test_database):
    """
    Fixture providing a database session for direct database access in tests.
    
    Use this when you need to set up specific test data or verify database state.
    
    Example:
        def test_order_saved(db_session, client):
            # Make API call
            response = client.post("/orders", json={...})
            
            # Verify in database
            order = db_session.query(OrderModel).first()
            assert order is not None
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
