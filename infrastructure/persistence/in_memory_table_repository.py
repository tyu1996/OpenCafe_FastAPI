# Import List and Optional for type hints
from typing import List, Optional

# Import the repository interface (port) we're implementing
from domain.repositories.table_repository import TableRepository

# Import the domain entity we're storing
from domain.entities.table import Table


class InMemoryTableRepository(TableRepository):
    """
    In-memory implementation of TableRepository.

    This is an ADAPTER that implements the TableRepository PORT.
    Uses a Python dictionary to store tables (in RAM, lost on restart).

    WHY IN-MEMORY STORAGE?
    - Learning focus: Understand clean architecture without database complexity
    - Fast development: No database setup, migrations, or connections
    - Easy testing: Create fresh repository for each test, no cleanup needed
    - Immediate results: System works out-of-the-box with sample data

    Real-world analogy: Think of this like a whiteboard with table assignments.
    It works great for a small cafe during one shift (development),
    but you'd want a reservation system (database) for long-term bookings.

    STORAGE STRUCTURE:
    Dictionary with table ID as key, Table object as value:
    {
        "table-001": Table(id="table-001", number=1, capacity=2, location="window"),
        "table-002": Table(id="table-002", number=2, capacity=4, location="main-room"),
    }
    """

    def __init__(self):
        """
        Initialize the repository with sample cafe tables.

        We create a realistic set of tables representing a small cafe:
        - Mix of sizes (2-person, 4-person, 6-person)
        - Different locations (window, patio, main room)
        - Representative of a typical cafe layout

        This sample data makes the API immediately testable.
        """
        # Store tables in a dictionary
        # Key = table ID (for fast lookup by ID)
        # Value = Table object (domain entity)
        self._tables = {
            # Table 1: Small table by the window
            # Perfect for 1-2 people, popular spot
            "table-001": Table(
                id="table-001",  # Unique identifier
                number=1,  # Table number displayed to customers
                capacity=2,  # Seats 2 people
                location="window",  # Prime location with natural light
            ),
            # Table 2: Medium table in main dining area
            # Good for small groups or families
            "table-002": Table(
                id="table-002",
                number=2,
                capacity=4,  # Seats 4 people
                location="main-room",  # Central location
            ),
            # Table 3: Small table by another window
            # Another 2-person spot with nice view
            "table-003": Table(
                id="table-003",
                number=3,
                capacity=2,
                location="window",
            ),
            # Table 4: Outdoor patio table
            # Weather-dependent seating option
            "table-004": Table(
                id="table-004",
                number=4,
                capacity=4,
                location="patio",  # Outdoor seating
            ),
            # Table 5: Large table for groups
            # Best for parties or business meetings
            "table-005": Table(
                id="table-005",
                number=5,
                capacity=6,  # Seats 6 people - our largest table
                location="main-room",
            ),
            # Table 6: Medium table in main area
            # Another 4-person option
            "table-006": Table(
                id="table-006",
                number=6,
                capacity=4,
                location="main-room",
            ),
        }

        # Total capacity: 2+4+2+4+6+4 = 22 people
        # Mix of locations: 2 window, 1 patio, 3 main-room
        # This represents a small neighborhood cafe

    def list_all_tables(self) -> List[Table]:
        """
        Get all tables from memory.

        Implementation: Return all Table objects from the dictionary.

        Returns:
            List[Table]: All 6 tables from our sample data
        """
        # self._tables.values() returns all Table objects
        # list(...) converts dict_values view to a list
        # Returns a NEW list so caller can modify without affecting storage
        return list(self._tables.values())

    def get_table_by_id(self, table_id: str) -> Optional[Table]:
        """
        Get a single table by ID from memory.

        Implementation: Dictionary lookup with safe None return.

        Args:
            table_id (str): The table ID to find (e.g., "table-001")

        Returns:
            Optional[Table]: The table if found, None if not found

        Examples:
            table = repo.get_table_by_id("table-001")  # Returns table
            table = repo.get_table_by_id("table-999")  # Returns None (doesn't exist)
        """
        # dict.get(key) returns value if key exists, None otherwise
        # Safer than self._tables[table_id] which raises KeyError if missing
        return self._tables.get(table_id)

    # Note: In Module 3, we'll replace this with SQLAlchemyTableRepository:
    # - list_all_tables() becomes: session.query(TableModel).all()
    # - get_table_by_id() becomes: session.query(TableModel).filter_by(id=table_id).first()
    #
    # But the TableRepository interface stays the same!
    # Use cases don't need to change at all.
    # That's the benefit of the ports & adapters pattern.
