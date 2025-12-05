# Import dataclass decorator - makes creating classes with data easier
from dataclasses import dataclass


@dataclass(frozen=True)  # frozen=True makes this immutable (cannot be changed after creation)
class Table:
    """
    Table represents a physical seating table in the cafe.

    This is a DOMAIN ENTITY - pure business logic with zero dependencies on frameworks.

    Real-world analogy: Think of this as a tag on a physical table in the cafe.
    It has a number (Table 5), capacity (seats 4 people), and location (by the window).

    Why immutable (frozen=True)?
    - Table properties (number, capacity, location) are fixed physical attributes
    - They don't change frequently in normal operations
    - Immutability makes the code more predictable
    - If you need to "change" a table, you create a new Table object
    """

    # Unique identifier for this table (like "table-001" or "tbl-5")
    id: str

    # Table number displayed to customers and staff (like 1, 2, 3, or "A1", "B2")
    # This is what waiters say: "Your order is for Table 5"
    number: int

    # Maximum number of people who can sit at this table
    # Important for seating management and availability
    capacity: int

    # Physical location description (like "window", "patio", "main-room")
    # Helps staff find the table and customers express preferences
    location: str

    def __post_init__(self):
        """
        Validation logic that runs automatically after __init__.

        This enforces BUSINESS RULES about what makes a valid table.
        These rules reflect real-world constraints of running a cafe.

        Why validate here?
        - These are domain rules that must ALWAYS be true
        - They apply regardless of how the table is created
        - Catching invalid data early prevents bugs downstream
        """

        # Business Rule #1: Table capacity must be positive
        # You can't have a table that seats 0 or negative people!
        # Real-world constraint: tables need to seat at least one person
        if self.capacity <= 0:
            raise ValueError("Table capacity must be greater than zero")

        # Business Rule #2: Table number must be positive
        # Table numbers typically start at 1, not 0 or negative
        # Real-world: "Table -3" makes no sense to staff or customers
        if self.number <= 0:
            raise ValueError("Table number must be greater than zero")

        # Note: We could add more validation:
        # - Maximum capacity limit (no table seats 1000 people)
        # - Location must be from predefined list
        # - Number must be unique (but that's enforced at repository level)
        # Keep it simple for now
