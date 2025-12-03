# Import pytest for test fixtures
import pytest

# Import FastAPI TestClient for integration testing
# TestClient lets us make HTTP requests to our API without running a server
from fastapi.testclient import TestClient

# Import our main FastAPI application
from main import app


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
"""


@pytest.fixture
def client():
    """
    Fixture that provides a FastAPI TestClient.

    Returns:
        TestClient: Client for making HTTP requests to the API

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

    WHEN THIS RUNS:
    - Pytest sees test needs 'client' parameter
    - Pytest looks for fixture named 'client'
    - Pytest calls this function
    - Pytest passes the return value to the test
    - After test finishes, pytest does any cleanup (none needed here)

    BENEFITS:
    - No need to start uvicorn server for tests
    - Tests run fast (no network overhead)
    - Tests are isolated (each test gets fresh client)
    - Can test API like an external client would use it
    """

    # Create a TestClient wrapping our FastAPI app
    # This client can make requests: GET, POST, PUT, DELETE, etc.
    # It follows the real HTTP protocol but runs in-process
    with TestClient(app) as test_client:
        # Yield the client to the test
        # 'yield' makes this a generator fixture
        # Everything before yield runs before the test
        # Everything after yield runs after the test (cleanup)
        yield test_client
    # When test finishes, the 'with' block closes the client
    # This ensures proper cleanup (close connections, etc.)

    # Alternative (simpler but no context manager):
    # return TestClient(app)
    # But using 'with' is better for resource management


# Future: we might add more fixtures
#
# @pytest.fixture
# def db_session():
#     """Fixture providing a database session."""
#     session = create_test_session()
#     yield session
#     session.close()
#
# @pytest.fixture
# def auth_headers():
#     """Fixture providing authentication headers."""
#     token = create_test_token()
#     return {"Authorization": f"Bearer {token}"}
#
# @pytest.fixture
# def sample_menu_item():
#     """Fixture providing a sample menu item."""
#     return MenuItem(
#         id="test-001",
#         name="Test Item",
#         description="For testing",
#         price=Decimal("1.00"),
#         category="test",
#         available=True
#     )
