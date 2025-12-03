# Import dataclass decorator - makes creating classes with data easier
# dataclass automatically generates __init__, __repr__, and other methods
from dataclasses import dataclass

# Import Decimal for precise money calculations
# Never use float for money! Decimal avoids rounding errors like 0.1 + 0.2 = 0.30000000000000004
from decimal import Decimal


@dataclass(frozen=True)  # frozen=True makes this immutable (cannot be changed after creation)
class MenuItem:
    """
    MenuItem represents a single item on the cafe menu.

    This is a DOMAIN ENTITY - pure business logic with zero dependencies on frameworks.
    It lives in the domain layer, so it has no knowledge of FastAPI, SQLAlchemy, or databases.

    Think of this as the "platonic ideal" of a menu item - the core business concept.
    """

    # Unique identifier for this menu item (like "item-001" or "espresso-latte")
    id: str

    # Display name of the item (like "Espresso" or "Cappuccino")
    name: str

    # Brief description shown to customers (like "Strong Italian coffee")
    description: str

    # Price in decimal format for exact money calculations
    # Example: Decimal("2.50") for $2.50
    price: Decimal

    # Category this item belongs to (like "coffee", "pastry", "sandwich")
    # Helps organize the menu and allows filtering
    category: str

    # Whether this item can currently be ordered
    # Default is True - most items are available
    # Set to False if temporarily out of stock
    available: bool = True

    def __post_init__(self):
        """
        Validation logic that runs automatically after __init__.

        This enforces BUSINESS RULES - the invariants that must always be true.
        These rules protect the integrity of our domain model.

        Why here and not in the API layer?
        - These are fundamental business rules, not just API validation
        - They apply no matter how we create menu items (API, tests, migrations, etc.)
        - The domain layer is the single source of truth for business logic
        """

        # Business Rule #1: Prices cannot be negative
        # You can't have a menu item that costs -$5 (that would mean paying customers!)
        if self.price < Decimal("0"):
            raise ValueError("Price cannot be negative")

        # Business Rule #2: Every item must have a non-empty name
        # strip() removes leading/trailing whitespace
        # A name like "   " (just spaces) is not valid
        if not self.name.strip():
            raise ValueError("Name cannot be empty")

        # Note: We could add more validation here:
        # - Description length limits
        # - Category must be from a valid set
        # - Price must have max 2 decimal places
        # But we keep it simple for now (KISS principle)
