# Import pytest for testing framework
import pytest


"""
Integration Tests for Tables API - Module 4

Tests verify:
- GET /tables returns all tables
- GET /tables/{id} returns specific table
- GET /tables/{id} returns 404 for invalid ID
- Response format and field validation

These are INTEGRATION tests - they test the full stack:
- API endpoint (routes/tables.py)
- Repository (infrastructure/persistence/sqlalchemy_table_repository.py)
- Database (SQLite with test data)
"""


class TestTablesAPI:
    """
    Test suite for Tables API endpoints.
    
    Test data (from conftest.py):
    - table-001: Table 1, capacity 2, window
    - table-002: Table 2, capacity 4, main-room
    - table-003: Table 3, capacity 4, patio
    - table-004: Table 4, capacity 6, main-room
    """

    # ===== LIST TABLES TESTS =====

    def test_list_tables_success(self, client):
        """Test listing all tables returns 200 and table data."""
        # Act: Request all tables
        response = client.get("/tables")

        # Assert: Success response
        assert response.status_code == 200

        # Assert: Returns a list
        tables = response.json()
        assert isinstance(tables, list)

        # Assert: Has expected tables from test data
        assert len(tables) >= 4, "Should have at least 4 tables from test data"

    def test_list_tables_response_format(self, client):
        """Test that table responses have all required fields."""
        # Act
        response = client.get("/tables")
        tables = response.json()

        # Assert: Each table has required fields
        required_fields = ["id", "number", "capacity", "location"]
        for table in tables:
            for field in required_fields:
                assert field in table, f"Missing required field: {field}"

    def test_list_tables_field_types(self, client):
        """Test that table fields have correct types."""
        # Act
        response = client.get("/tables")
        tables = response.json()

        # Assert: Correct types for first table
        if tables:
            table = tables[0]
            assert isinstance(table["id"], str)
            assert isinstance(table["number"], int)
            assert isinstance(table["capacity"], int)
            assert isinstance(table["location"], str)

    # ===== GET TABLE BY ID TESTS =====

    def test_get_table_by_id_success(self, client):
        """Test retrieving a specific table by ID."""
        # Arrange: Use known table ID from test data
        table_id = "table-001"

        # Act: Request specific table
        response = client.get(f"/tables/{table_id}")

        # Assert: Success response
        assert response.status_code == 200

        # Assert: Correct table returned
        table = response.json()
        assert table["id"] == table_id
        assert table["number"] == 1
        assert table["capacity"] == 2
        assert table["location"] == "window"

    def test_get_table_by_id_not_found(self, client):
        """Test retrieving non-existent table returns 404."""
        # Act: Request table that doesn't exist
        response = client.get("/tables/invalid-table-999")

        # Assert: 404 Not Found
        assert response.status_code == 404

        # Assert: Error message present
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
        assert "invalid-table-999" in data["detail"]

    def test_get_table_returns_all_fields(self, client):
        """Test that single table response has all fields."""
        # Act
        response = client.get("/tables/table-002")

        # Assert: All fields present
        assert response.status_code == 200
        table = response.json()

        required_fields = ["id", "number", "capacity", "location"]
        for field in required_fields:
            assert field in table, f"Missing field: {field}"

    # ===== RESPONSE FORMAT TESTS =====

    def test_list_response_is_array(self, client):
        """Test that list endpoint returns JSON array."""
        response = client.get("/tables")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_single_response_is_object(self, client):
        """Test that single table endpoint returns JSON object."""
        response = client.get("/tables/table-001")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    # ===== SPECIFIC TABLE DATA TESTS =====

    def test_table_data_accuracy(self, client):
        """Test that table data matches expected test data."""
        # Get all tables
        response = client.get("/tables")
        tables = response.json()

        # Find specific tables and verify data
        table_map = {t["id"]: t for t in tables}

        # Verify table-001
        if "table-001" in table_map:
            t1 = table_map["table-001"]
            assert t1["number"] == 1
            assert t1["capacity"] == 2
            assert t1["location"] == "window"

        # Verify table-004
        if "table-004" in table_map:
            t4 = table_map["table-004"]
            assert t4["number"] == 4
            assert t4["capacity"] == 6
            assert t4["location"] == "main-room"


    # ===== AREA FILTERING TESTS (MODULE 4) =====

    def test_filter_tables_by_area_window(self, client):
        """Test filtering tables by area=window returns only window tables."""
        # Act: Filter by window area
        response = client.get("/tables?area=window")

        # Assert: Success response
        assert response.status_code == 200

        # Assert: All returned tables are in window area
        tables = response.json()
        assert len(tables) >= 1, "Should have at least 1 window table"

        for table in tables:
            assert table["location"].lower() == "window", \
                f"Table {table['id']} should be in window area, got {table['location']}"

    def test_filter_tables_by_area_main_room(self, client):
        """Test filtering tables by area=main-room returns only main-room tables."""
        # Act: Filter by main-room area
        response = client.get("/tables?area=main-room")

        # Assert: Success response
        assert response.status_code == 200

        # Assert: All returned tables are in main-room area
        tables = response.json()
        assert len(tables) >= 1, "Should have at least 1 main-room table"

        for table in tables:
            assert table["location"].lower() == "main-room", \
                f"Table {table['id']} should be in main-room area, got {table['location']}"

    def test_filter_tables_by_area_patio(self, client):
        """Test filtering tables by area=patio returns only patio tables."""
        # Act: Filter by patio area
        response = client.get("/tables?area=patio")

        # Assert: Success response
        assert response.status_code == 200

        # Assert: All returned tables are in patio area
        tables = response.json()
        assert len(tables) >= 1, "Should have at least 1 patio table"

        for table in tables:
            assert table["location"].lower() == "patio", \
                f"Table {table['id']} should be in patio area, got {table['location']}"

    def test_filter_tables_by_area_case_insensitive(self, client):
        """Test that area filter is case-insensitive."""
        # Get tables with lowercase
        response_lower = client.get("/tables?area=window")
        tables_lower = response_lower.json()

        # Get tables with uppercase
        response_upper = client.get("/tables?area=WINDOW")
        tables_upper = response_upper.json()

        # Get tables with mixed case
        response_mixed = client.get("/tables?area=Window")
        tables_mixed = response_mixed.json()

        # Assert: All should return same number of tables
        assert len(tables_lower) == len(tables_upper) == len(tables_mixed), \
            "Area filter should be case-insensitive"

    def test_filter_tables_by_nonexistent_area(self, client):
        """Test filtering by non-existent area returns empty list."""
        # Act: Filter by area that doesn't exist
        response = client.get("/tables?area=rooftop")

        # Assert: Success response with empty list
        assert response.status_code == 200
        tables = response.json()
        assert tables == [], "Non-existent area should return empty list"

    def test_filter_tables_no_area_returns_all(self, client):
        """Test that not providing area filter returns all tables."""
        # Get all tables (no filter)
        response_all = client.get("/tables")
        all_tables = response_all.json()

        # Get tables with area filter
        response_window = client.get("/tables?area=window")
        response_main = client.get("/tables?area=main-room")
        response_patio = client.get("/tables?area=patio")

        window_tables = response_window.json()
        main_tables = response_main.json()
        patio_tables = response_patio.json()

        # Assert: Total of filtered tables should equal all tables
        # (assuming all tables have one of these three locations in test data)
        filtered_count = len(window_tables) + len(main_tables) + len(patio_tables)
        assert len(all_tables) == filtered_count, \
            f"All tables ({len(all_tables)}) should equal sum of filtered tables ({filtered_count})"


# MODULE 4 TABLE TESTS SUMMARY:
# These tests verify:
# ✓ GET /tables returns all tables
# ✓ GET /tables response has correct format
# ✓ GET /tables/{id} returns specific table
# ✓ GET /tables/{id} returns 404 for missing table
# ✓ Response field types are correct
# ✓ Table data matches expected values
# ✓ GET /tables?area=X filters by area (MODULE 4)
# ✓ Area filter is case-insensitive (MODULE 4)
# ✓ Non-existent area returns empty list (MODULE 4)
