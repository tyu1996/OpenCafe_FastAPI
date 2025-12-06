# Import pytest for testing
import pytest

# Import Decimal for checking prices
from decimal import Decimal


"""
Integration Tests for Menu API

WHAT ARE INTEGRATION TESTS?
- Test multiple components working together
- Test the full stack: API -> use case -> repository -> database
- Test HTTP layer: routes, status codes, JSON serialization
- More comprehensive than unit tests
- Slower than unit tests (but still fast!)

UNIT vs INTEGRATION:
- Unit tests: test one component in isolation (use fakes/mocks)
- Integration tests: test multiple real components together
- Unit: "Does this use case work?" Integration: "Does the API endpoint work?"

WHY BOTH?
- Unit tests: find bugs fast, test edge cases cheaply
- Integration tests: verify components integrate correctly
- Unit: test the parts. Integration: test the whole.

MODULE 3 UPDATE:
- Tests now run against in-memory SQLite test database (not production)
- Test database is seeded with consistent test data via conftest.py
- Dependencies are overridden to use test database
- Tests verify the full stack including database persistence

THESE TESTS:
- Use TestClient to make real HTTP requests
- Hit actual API endpoints backed by real database
- Test the full request/response cycle
- Verify JSON structure
- Check status codes
- Test query parameters
"""


class TestMenuAPI:
    """
    Integration test suite for menu endpoints.

    Tests HTTP layer behavior:
    - Do endpoints respond?
    - Are status codes correct?
    - Is JSON format correct?
    - Do query parameters work?
    """

    def test_list_menu_items_returns_200(self, client):
        """
        Test that GET /menu/items returns 200 OK.

        This is a smoke test: does the endpoint work at all?

        Args:
            client: TestClient fixture (from conftest.py)
        """
        # Act: Make HTTP GET request to /menu/items
        # client.get() simulates a browser or API client making the request
        response = client.get("/menu/items")

        # Assert: Response should be 200 OK (success)
        # 200 means the request was successful
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        # If this fails, the endpoint doesn't work at all

    def test_list_menu_items_returns_json_array(self, client):
        """
        Test that response is a JSON array.

        Verifies the response format is correct.
        """
        # Act: Get the menu items
        response = client.get("/menu/items")

        # Assert: Response body should be JSON array (list)
        # response.json() parses the JSON response body
        data = response.json()
        assert isinstance(data, list), "Response should be a JSON array"
        # We expect: [{...}, {...}, ...]

    def test_list_menu_items_returns_expected_fields(self, client):
        """
        Test that each item has all required fields with correct types.

        This verifies the response model structure.
        """
        # Act: Get the menu items
        response = client.get("/menu/items")
        items = response.json()

        # Assert: Should have at least one item (we pre-populated repository)
        assert len(items) > 0, "Should return at least one menu item"

        # Check the first item has all expected fields
        first_item = items[0]

        # Required fields (from MenuItemResponse model)
        assert "id" in first_item, "Item should have 'id' field"
        assert "name" in first_item, "Item should have 'name' field"
        assert "description" in first_item, "Item should have 'description' field"
        assert "price" in first_item, "Item should have 'price' field"
        assert "category" in first_item, "Item should have 'category' field"
        assert "available" in first_item, "Item should have 'available' field"

        # Check field types
        assert isinstance(first_item["id"], str), "id should be string"
        assert isinstance(first_item["name"], str), "name should be string"
        assert isinstance(first_item["description"], str), "description should be string"
        # Price is returned as float in JSON (Decimal -> float conversion)
        assert isinstance(first_item["price"], (int, float)), "price should be number"
        assert isinstance(first_item["category"], str), "category should be string"
        assert isinstance(first_item["available"], bool), "available should be boolean"

    def test_list_menu_items_with_only_available_true(self, client):
        """
        Test filtering to only available items (default behavior).

        Verifies that only_available=true (default) filters correctly.
        """
        # Act: Request only available items (this is the default)
        # Could explicitly use: /menu/items?only_available=true
        response = client.get("/menu/items")
        items = response.json()

        # Assert: All returned items should have available=true
        for item in items:
            assert item["available"] is True, f"Item {item['name']} should be available"

        # We should get fewer items than the total (some are unavailable)
        # Test database has 6 items, 1 is unavailable (seeded in conftest.py)
        # So we should get 5 available items
        assert len(items) == 5, "Should return only available items (5 out of 6)"

    def test_list_menu_items_with_only_available_false(self, client):
        """
        Test that only_available=false returns all items including unavailable.

        Verifies query parameter works correctly.
        """
        # Act: Request all items including unavailable
        # Query parameter: ?only_available=false
        response = client.get("/menu/items?only_available=false")
        items = response.json()

        # Assert: Should include items with available=false
        # Check if any item has available=false
        has_unavailable = any(item["available"] is False for item in items)
        assert has_unavailable, "Should include unavailable items when only_available=false"

        # Should get all 6 items from test database
        assert len(items) == 6, "Should return all items (6 total)"

    def test_list_menu_items_includes_expected_sample_data(self, client):
        """
        Test that response includes our pre-populated sample data.

        This verifies the repository integration works.
        """
        # Act: Get available menu items
        response = client.get("/menu/items")
        items = response.json()

        # Assert: Should include our sample items
        # Extract names from response
        item_names = [item["name"] for item in items]

        # Check for specific items we know exist in test database (seeded in conftest.py)
        assert "Espresso" in item_names, "Should include Espresso"
        assert "Cappuccino" in item_names, "Should include Cappuccino"
        assert "Croissant" in item_names, "Should include Croissant"

        # Check that unavailable item is NOT included (only_available=true by default)
        assert "Seasonal Special" not in item_names, "Should not include unavailable items by default"

    def test_list_menu_items_prices_are_valid(self, client):
        """
        Test that all prices are positive numbers.

        Verifies business rule: prices can't be negative.
        """
        # Act: Get menu items
        response = client.get("/menu/items?only_available=false")  # Get all items
        items = response.json()

        # Assert: All prices should be >= 0
        for item in items:
            price = item["price"]
            assert price >= 0, f"Price for {item['name']} cannot be negative: {price}"

    def test_health_endpoint_returns_200(self, client):
        """
        Test that health check endpoint works.

        While we're testing, verify the health endpoint too.
        """
        # Act: Request health endpoint
        response = client.get("/health")

        # Assert: Should return 200 OK
        assert response.status_code == 200, "Health endpoint should return 200"

        # Assert: Response should have expected fields
        data = response.json()
        assert "status" in data, "Health response should have 'status' field"
        assert "database" in data, "Health response should have 'database' field"

        # Status should be "healthy"
        assert data["status"] == "healthy", "API should report as healthy"

    def test_root_endpoint_returns_welcome_message(self, client):
        """
        Test that root endpoint (/) works.

        Verifies API discovery endpoint.
        """
        # Act: Request root endpoint
        response = client.get("/")

        # Assert: Should return 200 OK
        assert response.status_code == 200, "Root endpoint should return 200"

        # Assert: Should have welcome message
        data = response.json()
        assert "message" in data, "Root should have 'message' field"
        assert "version" in data, "Root should have 'version' field"
        assert "endpoints" in data, "Root should have 'endpoints' field"

        # Version should be 0.4.0 (Module 3)
        assert data["version"] == "0.4.0", "Version should be 0.4.0"

    def test_openapi_docs_endpoint_works(self, client):
        """
        Test that /docs endpoint is accessible.

        FastAPI auto-generates interactive API documentation.
        """
        # Act: Request /docs endpoint
        response = client.get("/docs")

        # Assert: Should return 200 OK (HTML page)
        # /docs returns HTML, not JSON
        assert response.status_code == 200, "/docs endpoint should work"

        # Content-Type should be HTML
        assert "text/html" in response.headers.get("content-type", ""), \
            "/docs should return HTML"


# What have these tests verified?
# ✓ Endpoints respond with correct status codes
# ✓ Response format is correct (JSON array with expected fields)
# ✓ Query parameters work (only_available filtering)
# ✓ Integration works (API -> use case -> repository)
# ✓ Business rules enforced (prices non-negative)
# ✓ Sample data loaded correctly
# ✓ All layers work together (full stack test)

# What these tests DON'T verify (that's what unit tests do):
# ✗ Internal use case logic details
# ✗ Repository implementation details
# ✗ Domain entity validation details
# ✗ Edge cases in business logic
# That's fine! Different test levels have different purposes.
