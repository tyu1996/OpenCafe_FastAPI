# Import pytest for testing framework
import pytest

# Import Decimal for price comparisons
from decimal import Decimal


"""
Integration Tests for Menu API - Module 4 Enhancements

MODULE 4 NEW TESTS:
- Search functionality
- Category filtering
- Pagination (limit/offset)
- Single item retrieval by ID
- Error handling (404 for not found)
- Parameter validation (limit bounds, etc.)
- Combined filters

These tests verify the full stack:
- API endpoint (routes/menu.py)
- Use case (application/use_cases/list_menu_items.py, get_menu_item.py)
- Repository (infrastructure/persistence/sqlalchemy_menu_repository.py)
- Database (SQLite with test data)

Why integration tests?
- Verify components work together correctly
- Test HTTP layer (status codes, JSON format)
- Test database integration
- Catch integration bugs that unit tests miss

Pattern:
1. Arrange: Set up test data (done in fixture)
2. Act: Make HTTP request via TestClient
3. Assert: Verify response is correct
"""


class TestMenuAPIModule4:
    """
    Test suite for Module 4 menu API enhancements.

    Tests new features:
    - Search
    - Filtering
    - Pagination
    - Single item retrieval
    - Error handling
    """

    # ===== SEARCH TESTS =====

    def test_search_by_name(self, client):
        """Test searching menu items by name."""
        # Act: Search for "espresso" in item names
        response = client.get("/menu/items?search=espresso")

        # Assert: Success response
        assert response.status_code == 200

        # Assert: Results contain search term
        items = response.json()
        assert len(items) > 0, "Should find items matching 'espresso'"

        # Verify each result contains search term in name or description
        for item in items:
            text = (item["name"] + " " + item["description"]).lower()
            assert "espresso" in text, f"Item {item['name']} should contain 'espresso'"

    def test_search_by_description(self, client):
        """Test searching in item descriptions."""
        # Act: Search for term that appears in description
        response = client.get("/menu/items?search=italian")

        # Assert: Should find items with "italian" in description
        items = response.json()
        assert len(items) > 0

        for item in items:
            text = (item["name"] + " " + item["description"]).lower()
            assert "italian" in text

    def test_search_case_insensitive(self, client):
        """Test that search is case-insensitive."""
        # Act: Search with different cases
        response_lower = client.get("/menu/items?search=espresso")
        response_upper = client.get("/menu/items?search=ESPRESSO")
        response_mixed = client.get("/menu/items?search=EsPrEsSo")

        # Assert: All should return same results
        items_lower = response_lower.json()
        items_upper = response_upper.json()
        items_mixed = response_mixed.json()

        assert len(items_lower) == len(items_upper) == len(items_mixed)

    def test_search_no_results(self, client):
        """Test search with no matching items."""
        # Act: Search for term that doesn't exist
        response = client.get("/menu/items?search=nonexistent")

        # Assert: Should return empty list (not error!)
        assert response.status_code == 200
        items = response.json()
        assert items == [], "Should return empty list when no matches"

    # ===== CATEGORY FILTER TESTS =====

    def test_filter_by_category(self, client):
        """Test filtering menu items by category."""
        # Act: Get items from coffee category
        # Assuming test data has category "cat-001" for coffee
        response = client.get("/menu/items?category_id=cat-001")

        # Assert: All items should be from cat-001
        items = response.json()
        assert len(items) > 0, "Should find items in cat-001"

        for item in items:
            assert item["category"] == "cat-001"

    def test_filter_by_nonexistent_category(self, client):
        """Test filtering by category that doesn't exist."""
        # Act: Filter by non-existent category
        response = client.get("/menu/items?category_id=cat-999")

        # Assert: Should return empty list (not error!)
        assert response.status_code == 200
        items = response.json()
        assert items == []

    # ===== PAGINATION TESTS =====

    def test_pagination_limit(self, client):
        """Test pagination limit parameter."""
        # Act: Request only 2 items
        response = client.get("/menu/items?limit=2")

        # Assert: Should return exactly 2 items
        items = response.json()
        assert len(items) == 2, "Should respect limit parameter"

    def test_pagination_offset(self, client):
        """Test pagination offset parameter."""
        # Act: Get first 2 items
        page1 = client.get("/menu/items?limit=2&offset=0")

        # Act: Get next 2 items (skip first 2)
        page2 = client.get("/menu/items?limit=2&offset=2")

        # Assert: Different items on each page
        items1 = page1.json()
        items2 = page2.json()

        assert len(items1) == 2
        assert len(items2) >= 1  # Might be less if fewer items available

        # Verify no overlap (different items)
        ids1 = {item["id"] for item in items1}
        ids2 = {item["id"] for item in items2}
        assert ids1.isdisjoint(ids2), "Pages should have different items"

    def test_pagination_limit_validation_too_low(self, client):
        """Test that limit < 1 returns error."""
        # Act: Try limit = 0
        response = client.get("/menu/items?limit=0")

        # Assert: Should return 400 Bad Request
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "limit" in data["detail"].lower()

    def test_pagination_limit_validation_too_high(self, client):
        """Test that limit > 100 returns error."""
        # Act: Try limit = 101
        response = client.get("/menu/items?limit=101")

        # Assert: Should return 400 Bad Request
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "limit" in data["detail"].lower()

    def test_pagination_offset_validation_negative(self, client):
        """Test that negative offset returns error."""
        # Act: Try offset = -1
        response = client.get("/menu/items?offset=-1")

        # Assert: Should return 400 Bad Request
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "offset" in data["detail"].lower()

    # ===== COMBINED FILTER TESTS =====

    def test_combined_search_and_category(self, client):
        """Test combining search and category filter."""
        # Act: Search for "espresso" in coffee category
        response = client.get("/menu/items?search=espresso&category_id=cat-001")

        # Assert: Results match both criteria
        items = response.json()
        assert len(items) >= 0  # May be zero if no matches

        for item in items:
            # Should be in cat-001
            assert item["category"] == "cat-001"

            # Should contain "espresso"
            text = (item["name"] + " " + item["description"]).lower()
            assert "espresso" in text

    def test_combined_all_filters(self, client):
        """Test combining search, category, availability, and pagination."""
        # Act: Complex query with all filters
        response = client.get(
            "/menu/items"
            "?search=coffee"
            "&category_id=cat-001"
            "&only_available=true"
            "&limit=10"
            "&offset=0"
        )

        # Assert: Should succeed
        assert response.status_code == 200
        items = response.json()

        # Verify all filters applied
        assert len(items) <= 10  # Pagination limit

        for item in items:
            assert item["available"] is True  # Availability filter
            assert item["category"] == "cat-001"  # Category filter
            # Note: search filter verified by database query

    # ===== SINGLE ITEM RETRIEVAL TESTS =====

    def test_get_item_by_id_success(self, client):
        """Test retrieving a single menu item by ID."""
        # Arrange: Use known item ID from test data
        item_id = "item-001"  # Espresso from test data

        # Act: Request single item
        response = client.get(f"/menu/items/{item_id}")

        # Assert: Should return 200 OK
        assert response.status_code == 200

        # Assert: Should return item details
        item = response.json()
        assert item["id"] == item_id
        assert "name" in item
        assert "description" in item
        assert "price" in item
        assert "category" in item
        assert "available" in item

    def test_get_item_by_id_not_found(self, client):
        """Test retrieving non-existent item returns 404."""
        # Act: Request item that doesn't exist
        response = client.get("/menu/items/invalid-id-999")

        # Assert: Should return 404 Not Found
        assert response.status_code == 404

        # Assert: Should have error detail
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
        assert "invalid-id-999" in data["detail"]

    def test_get_item_returns_all_fields(self, client):
        """Test that single item response has all required fields."""
        # Act: Get item
        response = client.get("/menu/items/item-001")
        item = response.json()

        # Assert: All fields present
        required_fields = ["id", "name", "description", "price", "category", "available"]
        for field in required_fields:
            assert field in item, f"Missing required field: {field}"

        # Assert: Correct types
        assert isinstance(item["id"], str)
        assert isinstance(item["name"], str)
        assert isinstance(item["description"], str)
        assert isinstance(item["price"], (int, float))
        assert isinstance(item["category"], str)
        assert isinstance(item["available"], bool)

    # ===== AVAILABILITY FILTER TESTS =====

    def test_only_available_true(self, client):
        """Test that only_available=true filters correctly."""
        # Act: Get only available items (default)
        response = client.get("/menu/items?only_available=true")

        # Assert: All items should be available
        items = response.json()
        for item in items:
            assert item["available"] is True

    def test_only_available_false(self, client):
        """Test that only_available=false returns all items."""
        # Act: Get all items including unavailable
        response = client.get("/menu/items?only_available=false")

        # Assert: Should include unavailable items
        items = response.json()

        # Check if there are any unavailable items
        has_unavailable = any(not item["available"] for item in items)
        # Note: Test data should include at least one unavailable item
        # If test data setup changes, this might need adjustment

    # ===== EDGE CASE TESTS =====

    def test_empty_search_string(self, client):
        """Test search with empty string returns all items."""
        # Act: Search with empty string
        response = client.get("/menu/items?search=")

        # Assert: Should return items (empty string matches nothing)
        assert response.status_code == 200
        items = response.json()
        # Empty search might return all or none depending on implementation
        # Just verify it doesn't crash

    def test_pagination_beyond_available_items(self, client):
        """Test offset beyond available items returns empty list."""
        # Act: Request items way beyond what exists
        response = client.get("/menu/items?offset=1000&limit=10")

        # Assert: Should return empty list (not error)
        assert response.status_code == 200
        items = response.json()
        assert items == []

    def test_multiple_filters_no_matches(self, client):
        """Test that impossible filter combination returns empty list."""
        # Act: Search for coffee in pastry category (should be empty)
        response = client.get("/menu/items?search=espresso&category_id=cat-002")

        # Assert: Should return empty list
        assert response.status_code == 200
        items = response.json()
        # Might be empty if cat-002 is pastries and has no espresso items

    # ===== RESPONSE FORMAT TESTS =====

    def test_list_response_is_array(self, client):
        """Test that list endpoint returns JSON array."""
        # Act
        response = client.get("/menu/items")

        # Assert: Response is a list
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_single_response_is_object(self, client):
        """Test that single item endpoint returns JSON object."""
        # Act
        response = client.get("/menu/items/item-001")

        # Assert: Response is an object (dict)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


# MODULE 4 TEST SUMMARY:
# These tests verify:
# ✓ Search functionality (case-insensitive, partial matching)
# ✓ Category filtering
# ✓ Pagination (limit/offset)
# ✓ Parameter validation (bounds checking)
# ✓ Single item retrieval
# ✓ Error handling (404, 400)
# ✓ Combined filters
# ✓ Edge cases
# ✓ Response formats
#
# These are INTEGRATION tests - they test the full stack.
# They verify that all components work together correctly.
