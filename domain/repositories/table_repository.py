# Import ABC (Abstract Base Class) and abstractmethod for defining interfaces
from abc import ABC, abstractmethod

# Import List and Optional for type hints
from typing import List, Optional

# Import the domain entity this repository manages
from domain.entities.table import Table


class TableRepository(ABC):
    """
    TableRepository defines the interface (contract) for accessing cafe tables.

    This is a PORT in the ports & adapters pattern.
    It defines WHAT operations we need for managing table data,
    but not HOW they're implemented.

    WHY SEPARATE REPOSITORY FOR TABLES?
    - Single Responsibility: each repository manages one entity type
    - Clear boundaries: table operations are separate from menu or order operations
    - Easy testing: can test table logic independently
    - Flexibility: tables and menu items might use different storage strategies

    Real-world analogy: Think of this like a seating chart system.
    It specifies that we can "list all tables" and "find a specific table",
    but doesn't say whether the chart is physical paper or digital.
    """

    @abstractmethod
    def list_all_tables(self) -> List[Table]:
        """
        Get all tables in the cafe.

        This method retrieves every table that exists.
        Useful for showing seating capacity, choosing available tables, etc.

        Returns:
            List[Table]: List of all tables (may be empty if no tables configured)

        Use cases:
        - Display seating chart to host/hostess
        - Check total capacity of cafe
        - Find available tables (combine with order data)

        Implementation notes for adapters:
        - Return an empty list if no tables exist (don't return None)
        - Don't filter - return ALL tables (available or occupied)
        - Don't sort - return in storage order (caller can sort if needed)
        """
        pass  # Abstract method - no implementation here

    @abstractmethod
    def list_tables(self, area: str | None = None) -> List[Table]:
        """
        Get tables with optional area filtering.

        MODULE 4 ENHANCEMENT: Added filtering by location/area.

        This method supports filtering tables by their physical location.
        Useful for helping customers choose their preferred seating area.

        Args:
            area (str | None): Filter by table location (e.g., "window", "patio", "main-room").
                              If None, return all tables (same as list_all_tables).

        Returns:
            List[Table]: List of tables matching the filter (may be empty)

        Use cases:
        - Customer wants to sit by the window
        - Staff viewing tables in specific area
        - Filtering seating options by preference

        Implementation notes for adapters:
        - Return an empty list if no tables match (don't return None)
        - Area comparison should be case-insensitive for better UX
        - If area is None, return all tables
        """
        pass  # Abstract method - no implementation here

    @abstractmethod
    def get_table_by_id(self, table_id: str) -> Optional[Table]:
        """
        Get a single table by its unique ID.

        This method looks up one specific table.
        Used when placing orders (need to verify table exists),
        checking table details, or managing specific table.

        Args:
            table_id (str): The unique identifier of the table to retrieve
                           Example: "table-001" or "tbl-5"

        Returns:
            Optional[Table]: The table if found, None if not found

        Why Optional?
        - Not all IDs exist (invalid, typos, deleted tables)
        - None clearly indicates "table not found"
        - Caller can handle: if table is None: raise HTTPException(404)

        Use cases:
        - Validate table exists before placing order
        - Show table details to staff
        - Check table capacity before seating party

        Implementation notes for adapters:
        - Return None if table doesn't exist (don't raise exception)
        - ID comparison should be case-sensitive
        - Return a full Table object with all fields populated
        """
        pass  # Abstract method - no implementation here

    # Note: In a full implementation, we might also have:
    # - save_table(table: Table) -> None
    # - delete_table(table_id: str) -> None
    # - find_tables_by_capacity(min_capacity: int) -> List[Table]
    # - find_tables_by_location(location: str) -> List[Table]
    # But we keep it simple for Module 2 (read-only operations)
