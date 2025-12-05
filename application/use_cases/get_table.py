# Import Optional for type hints
# Optional[Table] means "either a Table or None"
from typing import Optional

# Import the domain entity this use case works with
from domain.entities.table import Table

# Import the repository interface (port)
from domain.repositories.table_repository import TableRepository


class GetTable:
    """
    Use case for retrieving a single table by ID.

    WHAT IS A USE CASE?
    - Represents one business operation: "get table details"
    - Thin wrapper around repository call in this simple case
    - More complex use cases add business logic (this one is minimal)

    WHY THIS USE CASE?
    - Validate table exists before placing order
    - Show table details to staff
    - Check table capacity before seating
    - Part of order placement workflow

    Real-world analogy: Looking up a specific table in the seating chart.
    You know the table number/ID, and you want its full details.

    SINGLE RESPONSIBILITY:
    This use case does ONE thing: get table by ID.
    It doesn't list tables, create tables, or update tables.
    Each operation is a separate use case.

    WHY SO THIN?
    You might wonder: "Why not just call the repository directly?"
    Good question! Here's why we still use a use case:
    1. Consistency: all operations go through use cases
    2. Future extensibility: easy to add logic later
    3. Testing: consistent testing pattern
    4. Logging/monitoring: single place to add instrumentation

    Later, this use case might grow to:
    - Check if table has active orders
    - Log table access for analytics
    - Check user permissions
    - Add caching
    But we start simple!
    """

    def __init__(self, table_repository: TableRepository):
        """
        Initialize the use case with its dependencies.

        Args:
            table_repository (TableRepository): Repository for accessing tables
                Type is the INTERFACE (not concrete implementation)
                This enables dependency injection and testing
        """
        # Store repository for later use
        # Private attribute (underscore prefix)
        self._table_repository = table_repository

    def execute(self, table_id: str) -> Optional[Table]:
        """
        Execute the use case: get table by ID.

        This is a simple "pass-through" use case.
        It delegates directly to the repository with no additional logic.

        Args:
            table_id (str): The unique ID of the table to retrieve
                           Example: "table-001", "tbl-5"

        Returns:
            Optional[Table]: The table if found, None if not found

        Why Optional?
        - Not all IDs exist (invalid, typo, deleted)
        - None clearly indicates "not found" without exception
        - Caller decides how to handle (404 response, error message, etc.)

        Algorithm:
        1. Call repository to get table by ID
        2. Return whatever repository returns (Table or None)

        That's it! Very simple.
        """

        # Delegate to repository
        # Repository handles the actual lookup (memory, database, etc.)
        # We just pass through the request
        table = self._table_repository.get_table_by_id(table_id)

        # Return result (either Table or None)
        return table

        # Note: In a more complex system, we might add logic here:
        # - if table is None: raise TableNotFoundException(table_id)
        # - Log access: logger.info(f"Table {table_id} accessed")
        # - Check permissions: if not user.can_view_table(table): raise Forbidden()
        # - Enrich data: table.has_active_orders = check_orders(table_id)
        # But we keep it simple for Module 2

    # ALTERNATIVE DESIGN:
    # Some developers prefer to raise an exception instead of returning None:
    #
    # def execute(self, table_id: str) -> Table:
    #     table = self._table_repository.get_table_by_id(table_id)
    #     if table is None:
    #         raise ValueError(f"Table {table_id} not found")
    #     return table
    #
    # Both approaches are valid. We use Optional for this module.

    # TESTING NOTE:
    # Easy to test without FastAPI or database:
    #
    # def test_get_existing_table():
    #     table = Table(id="table-001", number=1, capacity=2, location="window")
    #     fake_repo = FakeTableRepository([table])
    #     use_case = GetTable(fake_repo)
    #
    #     result = use_case.execute("table-001")
    #
    #     assert result is not None
    #     assert result.id == "table-001"
    #
    # def test_get_nonexistent_table():
    #     fake_repo = FakeTableRepository([])
    #     use_case = GetTable(fake_repo)
    #
    #     result = use_case.execute("table-999")
    #
    #     assert result is None
