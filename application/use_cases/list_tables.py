# Import List for type hints
# List[Table] means "a list containing Table objects"
from typing import List

# Import the Table domain entity
# Use cases work with domain entities
from domain.entities.table import Table

# Import the TableRepository port (interface)
# Notice: we import the INTERFACE, not a concrete implementation
# This is the Dependency Inversion Principle in action
from domain.repositories.table_repository import TableRepository


class ListTables:
    """
    Use case for listing tables with optional filtering.

    MODULE 4 ENHANCEMENT: Added area filtering to support browsing tables by location.

    WHAT IS A USE CASE?
    - A use case represents one business operation: "list cafe tables"
    - Coordinates between domain entities and repositories
    - Contains APPLICATION logic, not domain logic

    WHY THIS USE CASE?
    - Display all tables or filter by area (window, patio, main-room)
    - Help customers choose seating preference
    - Staff can view tables in specific areas

    SINGLE RESPONSIBILITY:
    This use case does ONE thing: list tables (with optional filtering).
    Getting a single table is a separate use case (GetTable).
    """

    def __init__(self, table_repository: TableRepository):
        """
        Initialize the use case with its dependencies.

        Args:
            table_repository (TableRepository): The repository to fetch tables from
                Notice the type hint is the INTERFACE, not a concrete class
                This means any class that implements TableRepository will work
        """
        # Store the repository for later use
        # Convention: private attribute starts with underscore
        self._table_repository = table_repository

    def execute(self, area: str | None = None) -> List[Table]:
        """
        Execute the use case: list tables with optional area filtering.

        MODULE 4 ENHANCEMENT: Added area filter parameter.
        - If area is None, return all tables
        - If area is provided, return only tables in that area

        Args:
            area (str | None): Filter by table location/area (e.g., "window", "patio").
                              None means return all tables.

        Returns:
            List[Table]: List of tables matching filter (may be empty)

        Example:
            # Get all tables
            tables = use_case.execute()

            # Get only patio tables
            patio_tables = use_case.execute(area="patio")

            # Get window tables
            window_tables = use_case.execute(area="window")
        """

        # Call repository to get tables with optional area filter
        # Repository handles the actual filtering (database-level or in-memory)
        tables = self._table_repository.list_tables(area=area)

        # Return the filtered tables
        return tables
