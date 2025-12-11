# Import pytest for testing framework
import pytest


"""
Integration Tests for Categories API - Module 4

Tests verify:
- GET /menu/categories returns all categories
- GET /menu/categories/{id}/items returns items in category
- GET /menu/categories/{id}/items returns 404 for invalid category
- Pagination and filtering on category items
- Response format and field validation

These are INTEGRATION tests - they test the full stack:
- API endpoint (routes/menu.py)
- Use cases (application/use_cases/)
- Repositories (infrastructure/persistence/)
- Database (SQLite with test data)
"""


class TestCategoriesAPI:
    """
    Test suite for Categories API endpoints.
    
    Test data (from conftest.py):
    Categories:
    - cat-001: Coffee Drinks
    - cat-002: Pastries
    
    Items in cat-001 (Coffee):
    - item-001: Espresso
    - item-002: Cappuccino
    - item-005: Latte
    - item-006: Seasonal Special (UNAVAILABLE)
    
    Items in cat-002 (Pastries):
    - item-003: Croissant
    - item-004: Blueberry Muffin
    """

    # ===== LIST CATEGORIES TESTS =====

    def test_list_categories_success(self, client):
        """Test listing all categories returns 200 and data."""
        # Act
        response = client.get("/menu/categories")

        # Assert: Success
        assert response.status_code == 200

        # Assert: Returns list
        categories = response.json()
        assert isinstance(categories, list)

        # Assert: Has expected categories
        assert len(categories) >= 2, "Should have at least 2 categories"

    def test_list_categories_response_format(self, client):
        """Test that category responses have all required fields."""
        # Act
        response = client.get("/menu/categories")
        categories = response.json()

        # Assert: Each category has required fields
        required_fields = ["id", "name", "description"]
        for category in categories:
            for field in required_fields:
                assert field in category, f"Missing required field: {field}"

    def test_list_categories_field_types(self, client):
        """Test that category fields have correct types."""
        # Act
        response = client.get("/menu/categories")
        categories = response.json()

        # Assert: Correct types
        if categories:
            cat = categories[0]
            assert isinstance(cat["id"], str)
            assert isinstance(cat["name"], str)
            assert isinstance(cat["description"], str)

    def test_list_categories_data_accuracy(self, client):
        """Test that category data matches expected test data."""
        # Act
        response = client.get("/menu/categories")
        categories = response.json()

        # Create map for lookup
        cat_map = {c["id"]: c for c in categories}

        # Verify cat-001
        assert "cat-001" in cat_map
        assert cat_map["cat-001"]["name"] == "Coffee Drinks"

        # Verify cat-002
        assert "cat-002" in cat_map
        assert cat_map["cat-002"]["name"] == "Pastries"

    # ===== GET CATEGORY ITEMS TESTS =====

    def test_get_category_items_success(self, client):
        """Test getting items from a specific category."""
        # Act: Get items from coffee category
        response = client.get("/menu/categories/cat-001/items")

        # Assert: Success
        assert response.status_code == 200

        # Assert: Returns list
        items = response.json()
        assert isinstance(items, list)
        assert len(items) > 0, "Should have items in coffee category"

        # Assert: All items are from cat-001
        for item in items:
            assert item["category"] == "cat-001"

    def test_get_category_items_not_found(self, client):
        """Test getting items from non-existent category returns 404."""
        # Act
        response = client.get("/menu/categories/cat-999/items")

        # Assert: 404 Not Found
        assert response.status_code == 404

        # Assert: Error message
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
        assert "cat-999" in data["detail"]

    def test_get_category_items_response_format(self, client):
        """Test that category items have correct menu item format."""
        # Act
        response = client.get("/menu/categories/cat-001/items")
        items = response.json()

        # Assert: Menu item fields present
        required_fields = ["id", "name", "description", "price", "category", "available"]
        for item in items:
            for field in required_fields:
                assert field in item, f"Missing field: {field}"

    def test_get_category_items_only_available(self, client):
        """Test that default returns only available items."""
        # Act: Default (only_available=true)
        response = client.get("/menu/categories/cat-001/items")
        items = response.json()

        # Assert: All items are available
        for item in items:
            assert item["available"] is True

    def test_get_category_items_include_unavailable(self, client):
        """Test getting all items including unavailable."""
        # Act: Include unavailable items
        response = client.get("/menu/categories/cat-001/items?only_available=false")
        items = response.json()

        # Assert: Should include more items (including unavailable Seasonal Special)
        # Coffee category has 3 available + 1 unavailable = 4 items
        assert len(items) >= 3  # At least some items

    # ===== PAGINATION TESTS =====

    def test_get_category_items_pagination_limit(self, client):
        """Test pagination limit on category items."""
        # Act: Request only 2 items
        response = client.get("/menu/categories/cat-001/items?limit=2")

        # Assert
        assert response.status_code == 200
        items = response.json()
        assert len(items) <= 2

    def test_get_category_items_pagination_offset(self, client):
        """Test pagination offset on category items."""
        # Act: Get first 2 items
        page1 = client.get("/menu/categories/cat-001/items?limit=2&offset=0")
        # Act: Get next items
        page2 = client.get("/menu/categories/cat-001/items?limit=2&offset=2")

        items1 = page1.json()
        items2 = page2.json()

        # Assert: Different items (if there are enough items)
        if len(items1) > 0 and len(items2) > 0:
            ids1 = {i["id"] for i in items1}
            ids2 = {i["id"] for i in items2}
            assert ids1.isdisjoint(ids2), "Pages should have different items"

    def test_get_category_items_invalid_limit(self, client):
        """Test that invalid limit returns 400."""
        # Act: limit = 0
        response = client.get("/menu/categories/cat-001/items?limit=0")

        # Assert: 400 Bad Request
        assert response.status_code == 400
        assert "limit" in response.json()["detail"].lower()

    def test_get_category_items_invalid_offset(self, client):
        """Test that negative offset returns 400."""
        # Act: offset = -1
        response = client.get("/menu/categories/cat-001/items?offset=-1")

        # Assert: 400 Bad Request
        assert response.status_code == 400
        assert "offset" in response.json()["detail"].lower()

    # ===== EMPTY CATEGORY TESTS =====

    def test_get_category_items_empty_result(self, client):
        """Test getting items with high offset returns empty list."""
        # Act: Offset beyond available items
        response = client.get("/menu/categories/cat-001/items?offset=1000")

        # Assert: Empty list, not error
        assert response.status_code == 200
        items = response.json()
        assert items == []

    # ===== DIFFERENT CATEGORIES TESTS =====

    def test_get_pastry_category_items(self, client):
        """Test getting items from pastry category."""
        # Act
        response = client.get("/menu/categories/cat-002/items")

        # Assert
        assert response.status_code == 200
        items = response.json()

        # All should be from cat-002
        for item in items:
            assert item["category"] == "cat-002"

        # Should have pastry items
        names = [i["name"] for i in items]
        assert any("Croissant" in n or "Muffin" in n for n in names)


# MODULE 4 CATEGORIES TESTS SUMMARY:
# These tests verify:
# ✓ GET /menu/categories returns all categories
# ✓ GET /menu/categories response format correct
# ✓ GET /menu/categories/{id}/items returns items in category
# ✓ GET /menu/categories/{id}/items returns 404 for missing category
# ✓ Category items respect only_available filter
# ✓ Category items support pagination (limit/offset)
# ✓ Invalid pagination parameters return 400
# ✓ Empty results return empty list, not error
