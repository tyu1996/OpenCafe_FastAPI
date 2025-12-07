# Import typing utilities
from typing import List, Dict, Optional

# Import Decimal for precise money calculations
from decimal import Decimal

# Import the domain entity and port
# Infrastructure layer knows about domain layer (dependency flows inward)
from domain.entities.menu import MenuItem
from domain.repositories.menu_repository import MenuRepository


class InMemoryMenuRepository(MenuRepository):
    """
    In-memory implementation of MenuRepository.

    This is an ADAPTER in the Ports & Adapters pattern:
    - The PORT is MenuRepository (the interface)
    - This ADAPTER provides a concrete implementation
    - Data is stored in memory (a Python dictionary)

    WHEN TO USE THIS:
    - Development and testing
    - Demos and prototypes
    - When you don't need data persistence
    - Early stages before database is ready

    WHY THIS IS USEFUL:
    - Super fast (no database I/O)
    - No external dependencies (no Postgres, no migrations)
    - Easy to understand (just a dict!)
    - Easy to swap later (change DI config, everything else stays the same)

    PRODUCTION ALTERNATIVE:
    - Later we'll create SQLAlchemyMenuRepository
    - It will implement the same MenuRepository interface
    - Application layer won't know the difference!
    - That's the power of ports & adapters

    Real-world analogy:
    - This is like a notepad for taking orders (temporary, in memory)
    - Later we'll upgrade to a proper cash register system (database)
    - But the waiter (application layer) doesn't care which system we use
    """

    def __init__(self):
        """
        Initialize the repository with sample menu items.

        We pre-populate with sample data so the API has something to show immediately.
        In a real system, this data would come from a database or be loaded from a file.
        """

        # Store items in a dictionary for O(1) lookup by ID
        # Key: item_id (string), Value: MenuItem object
        # Dict[str, MenuItem] means "dictionary with string keys and MenuItem values"
        self._items: Dict[str, MenuItem] = {}

        # Pre-populate with sample cafe items
        # This gives us realistic demo data

        # Coffee items
        self._items["item-001"] = MenuItem(
            id="item-001",  # Unique ID for this item
            name="Espresso",  # What customers see on the menu
            description="Strong Italian coffee",  # Brief explanation
            price=Decimal("2.50"),  # $2.50 - using Decimal for precision
            category="coffee",  # Group items by category
            available=True  # Currently available to order
        )

        self._items["item-002"] = MenuItem(
            id="item-002",
            name="Cappuccino",
            description="Espresso with steamed milk foam",
            price=Decimal("3.50"),  # $3.50
            category="coffee",
            available=True
        )

        self._items["item-003"] = MenuItem(
            id="item-003",
            name="Latte",
            description="Espresso with steamed milk",
            price=Decimal("4.00"),  # $4.00
            category="coffee",
            available=True
        )

        # Pastry items
        self._items["item-004"] = MenuItem(
            id="item-004",
            name="Croissant",
            description="Buttery French pastry",
            price=Decimal("2.75"),  # $2.75
            category="pastry",
            available=True
        )

        self._items["item-005"] = MenuItem(
            id="item-005",
            name="Chocolate Muffin",
            description="Moist chocolate muffin with chocolate chips",
            price=Decimal("3.25"),  # $3.25
            category="pastry",
            available=True
        )

        # An unavailable item (to demonstrate filtering)
        self._items["item-006"] = MenuItem(
            id="item-006",
            name="Seasonal Special",
            description="Limited time seasonal drink",
            price=Decimal("5.50"),  # $5.50
            category="coffee",
            available=False  # Currently out of stock / not in season
        )

        # Note: In a real system, we'd load this data from:
        # - A database (most common)
        # - A JSON file (for configuration)
        # - An external API (if syncing with another system)

    def list_all_items(self) -> List[MenuItem]:
        """
        Return all menu items in the repository.

        Implements the MenuRepository.list_all_items() contract.

        Returns:
            List[MenuItem]: All items, including unavailable ones

        Time complexity: O(n) where n is the number of items
        (We need to copy all items from the dict to a list)
        """

        # Convert dictionary values to a list
        # dict.values() gives us a view of all values
        # list() converts it to an actual list
        # This creates a new list (doesn't expose our internal dict)
        return list(self._items.values())

        # Why return a new list?
        # - Encapsulation: caller can't modify our internal _items dict
        # - Defensive copying: protect our data from external changes
        # - Contract: we promised to return a List, not a dict_values

    def get_item_by_id(self, item_id: str) -> Optional[MenuItem]:
        """
        Find and return a menu item by its ID.

        Implements the MenuRepository.get_item_by_id() contract.

        Args:
            item_id (str): The unique identifier of the item to find

        Returns:
            Optional[MenuItem]: The item if found, None if not found

        Time complexity: O(1) - dictionary lookup is constant time
        """

        # Use dict.get() for safe lookup
        # dict.get(key) returns the value if key exists, None if it doesn't
        # This is better than dict[key] which would raise KeyError if not found
        return self._items.get(item_id)

        # Alternative (less safe):
        # if item_id in self._items:
        #     return self._items[item_id]
        # else:
        #     return None

        # Why .get() is better:
        # - More concise
        # - Idiomatic Python
        # - No risk of KeyError exception

    def list_items(
        self,
        only_available: bool = True,
        category_id: str | None = None,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[MenuItem]:
        """
        List menu items with filtering, searching, and pagination.

        MODULE 4 NEW METHOD - In-memory implementation of enhanced querying.

        This does the same thing as SQLAlchemy version but with Python filtering.
        Less efficient than database filtering but works for testing and small datasets.

        Args:
            only_available: If True, filter to available items only
            category_id: If provided, filter to specific category
            search: If provided, search in name and description
            limit: Maximum items to return (pagination)
            offset: Items to skip (pagination)

        Returns:
            List[MenuItem]: Filtered menu items

        Time complexity: O(n) where n is total number of items
        (Must iterate through all items to filter)
        """
        # Start with all items
        # Convert dict values to list
        items = list(self._items.values())

        # FILTER 1: Availability (MODULE 4)
        # Keep only available items if only_available is True
        if only_available:
            # List comprehension: keep items where available is True
            items = [item for item in items if item.available]

        # FILTER 2: Category (MODULE 4)
        # Keep only items from specific category if category_id provided
        if category_id is not None:
            # List comprehension: keep items matching category
            items = [item for item in items if item.category == category_id]

        # FILTER 3: Search (MODULE 4)
        # Keep only items with search text in name or description
        if search is not None:
            # Convert search to lowercase for case-insensitive matching
            search_lower = search.lower()

            # List comprehension with complex condition
            # Keep item if search text appears in name OR description
            items = [
                item for item in items
                if (search_lower in item.name.lower() or
                    search_lower in item.description.lower())
            ]

        # PAGINATION (MODULE 4)
        # Slice the list to get the requested page
        # Example: offset=20, limit=10 returns items[20:30]
        # Python slicing: list[start:end] where end = start + limit
        items = items[offset:offset + limit]

        # Return the filtered and paginated list
        return items

        # Note: In-memory filtering is less efficient than database filtering
        # Database can use indexes and optimize queries
        # But in-memory is fine for testing and small datasets

    # Future methods we might add:
    # def add_item(self, item: MenuItem) -> None:
    #     """Add a new item to the menu."""
    #     self._items[item.id] = item
    #
    # def update_item(self, item: MenuItem) -> None:
    #     """Update an existing item."""
    #     if item.id in self._items:
    #         self._items[item.id] = item
    #     else:
    #         raise ValueError(f"Item {item.id} not found")
    #
    # def delete_item(self, item_id: str) -> None:
    #     """Remove an item from the menu."""
    #     if item_id in self._items:
    #         del self._items[item_id]
    #     else:
    #         raise ValueError(f"Item {item_id} not found")
    #
    # But for Module 1, we keep it simple - just reading, no mutations
