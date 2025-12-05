# Import List and Optional for type hints
from typing import List, Optional

# Import the repository interface (port) we're implementing
from domain.repositories.category_repository import CategoryRepository

# Import the domain entity we're storing
from domain.entities.category import MenuCategory


class InMemoryCategoryRepository(CategoryRepository):
    """
    In-memory implementation of CategoryRepository.

    This is an ADAPTER in the ports & adapters pattern.
    It implements the CategoryRepository PORT using a simple Python dictionary.

    WHY IN-MEMORY?
    - Simple to understand (no database setup needed)
    - Fast for development and testing
    - No external dependencies
    - Easy to reset between tests

    WHEN TO USE IN-MEMORY:
    - Module 1-2: Learning clean architecture patterns
    - Unit tests: Fast, isolated tests
    - Development: Quick iteration without database
    - Demos: Show the system working immediately

    WHEN TO REPLACE WITH DATABASE:
    - Module 3: Adding real persistence
    - Production: Need data to survive restarts
    - Multiple instances: Need shared data store

    Real-world analogy: Think of this like a notepad for categories.
    It works great for jotting down quick notes (development),
    but you need a filing system (database) for long-term storage.

    STORAGE STRUCTURE:
    We use a dictionary (dict) with category ID as key and MenuCategory as value:
    {
        "cat-001": MenuCategory(id="cat-001", name="Coffee Drinks", ...),
        "cat-002": MenuCategory(id="cat-002", name="Pastries", ...),
    }

    Why dictionary instead of list?
    - Fast lookup by ID: O(1) vs O(n)
    - Natural key-value relationship (ID → Category)
    - Easy to check if ID exists: "cat-001" in self._categories
    """

    def __init__(self):
        """
        Initialize the repository with sample data.

        We pre-populate with realistic cafe categories.
        This makes the API immediately usable without setup.

        In a real system, this data would come from:
        - Database seed scripts
        - Admin UI for creating categories
        - Data migration from existing system
        """
        # Store categories in a dictionary
        # Key = category ID (for fast lookup)
        # Value = MenuCategory object (domain entity)
        self._categories = {
            # Category 1: Coffee Drinks
            # Groups all hot and cold coffee beverages
            "cat-coffee": MenuCategory(
                id="cat-coffee",  # Unique identifier
                name="Coffee Drinks",  # Display name
                description="Hot and cold coffee beverages",  # Description for customers
            ),
            # Category 2: Pastries
            # Groups baked goods like croissants, muffins
            "cat-pastries": MenuCategory(
                id="cat-pastries",
                name="Pastries",
                description="Freshly baked pastries and sweet treats",
            ),
            # Category 3: Sandwiches
            # Groups lunch items
            "cat-sandwiches": MenuCategory(
                id="cat-sandwiches",
                name="Sandwiches",
                description="Sandwiches and lunch items",
            ),
            # Category 4: Breakfast
            # Groups morning items available until 11 AM
            "cat-breakfast": MenuCategory(
                id="cat-breakfast",
                name="Breakfast",
                description="Breakfast items available until 11 AM",
            ),
        }

    def list_all_categories(self) -> List[MenuCategory]:
        """
        Get all categories from memory.

        Implementation: Return all values from the dictionary as a list.

        Returns:
            List[MenuCategory]: All categories (4 categories in our sample data)
        """
        # self._categories.values() returns all MenuCategory objects
        # list(...) converts the dict_values view to a list
        # This returns a NEW list, so caller can modify it without affecting storage
        return list(self._categories.values())

    def get_category_by_id(self, category_id: str) -> Optional[MenuCategory]:
        """
        Get a single category by ID from memory.

        Implementation: Look up in dictionary, return None if not found.

        Args:
            category_id (str): The category ID to find (e.g., "cat-coffee")

        Returns:
            Optional[MenuCategory]: The category if found, None otherwise
        """
        # dict.get(key) returns the value if key exists, None if not
        # This is safer than self._categories[category_id] which would raise KeyError
        return self._categories.get(category_id)

    # Note: In Module 3, when we switch to SQLAlchemy, this class becomes:
    # class SQLAlchemyCategoryRepository(CategoryRepository):
    #     def list_all_categories(self):
    #         return session.query(CategoryModel).all()  # SQL query
    #     def get_category_by_id(self, category_id):
    #         return session.query(CategoryModel).filter_by(id=category_id).first()
    #
    # But the INTERFACE (CategoryRepository) stays the same!
    # That's the power of ports & adapters.
