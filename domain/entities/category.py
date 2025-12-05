# Import dataclass decorator - makes creating classes with data easier
# dataclass automatically generates __init__, __repr__, and other methods
from dataclasses import dataclass


@dataclass(frozen=True)  # frozen=True makes this immutable (cannot be changed after creation)
class MenuCategory:
    """
    MenuCategory represents a category that groups menu items together.

    This is a DOMAIN ENTITY - pure business logic with zero dependencies on frameworks.
    It lives in the domain layer, so it has no knowledge of FastAPI, SQLAlchemy, or databases.

    Real-world analogy: Think of menu categories like sections in a restaurant menu book.
    "Coffee Drinks", "Pastries", "Sandwiches" - each section helps organize items.

    Why immutable (frozen=True)?
    - Categories rarely change once created
    - Immutability prevents accidental modifications
    - Safe to use as dictionary keys or in sets
    - Makes code more predictable and easier to reason about
    """

    # Unique identifier for this category (like "cat-001" or "coffee-drinks")
    id: str

    # Display name of the category (like "Coffee Drinks" or "Breakfast Items")
    name: str

    # Brief description of what items belong in this category
    # Example: "Hot and cold coffee beverages" or "Available until 11 AM"
    description: str

    def __post_init__(self):
        """
        Validation logic that runs automatically after __init__.

        This enforces BUSINESS RULES - the invariants that must always be true.
        These rules protect the integrity of our domain model.

        Why validate here?
        - These are fundamental business rules, not just API validation
        - They apply no matter how we create categories (API, tests, migrations, etc.)
        - The domain layer is the single source of truth for business logic
        """

        # Business Rule #1: Every category must have a non-empty name
        # strip() removes leading/trailing whitespace
        # A name like "   " (just spaces) is not valid
        if not self.name.strip():
            raise ValueError("Category name cannot be empty")

        # Note: We could add more validation here:
        # - Description length limits
        # - Name length constraints
        # - Character restrictions (no special characters, etc.)
        # But we keep it simple for now (KISS principle)
