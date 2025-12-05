# Import ABC (Abstract Base Class) and abstractmethod for defining interfaces
# ABC lets us create abstract classes that can't be instantiated directly
# abstractmethod marks methods that MUST be implemented by subclasses
from abc import ABC, abstractmethod

# Import List and Optional for type hints
# List[MenuCategory] means "a list containing MenuCategory objects"
# Optional[MenuCategory] means "either a MenuCategory or None"
from typing import List, Optional

# Import the domain entity this repository manages
from domain.entities.category import MenuCategory


class CategoryRepository(ABC):
    """
    CategoryRepository defines the interface (contract) for accessing menu categories.

    This is a PORT in the ports & adapters pattern.
    It lives in the domain layer and defines WHAT operations we need,
    but not HOW they're implemented.

    WHY AN INTERFACE?
    - Decoupling: domain doesn't depend on infrastructure (database, storage, etc.)
    - Testability: tests can use fake implementations (no real database needed)
    - Flexibility: swap implementations (in-memory → PostgreSQL → MongoDB) easily
    - Clear contract: anyone can see what operations are available

    Real-world analogy: Think of this like a restaurant's inventory system specification.
    It says "we need to list all categories and find categories by ID",
    but doesn't specify whether we use a filing cabinet, computer, or cloud database.

    NAMING CONVENTION:
    - Repository classes use the entity name + "Repository"
    - Methods use clear, descriptive names (list_all, get_by_id, save, delete)
    """

    @abstractmethod
    def list_all_categories(self) -> List[MenuCategory]:
        """
        Get all menu categories.

        This method retrieves every category that exists in the system.
        Useful for displaying the full menu structure to customers or staff.

        Returns:
            List[MenuCategory]: List of all categories (may be empty if none exist)

        Implementation notes for adapters:
        - Return an empty list if no categories exist (don't return None)
        - Don't filter or sort - return ALL categories as-is
        - Each returned MenuCategory must be a valid domain entity
        """
        pass  # Abstract method - no implementation here

    @abstractmethod
    def get_category_by_id(self, category_id: str) -> Optional[MenuCategory]:
        """
        Get a single category by its unique ID.

        This method looks up one specific category.
        Used when you know the category ID and need its details.

        Args:
            category_id (str): The unique identifier of the category to retrieve
                             Example: "cat-001" or "coffee-drinks"

        Returns:
            Optional[MenuCategory]: The category if found, None if not found

        Why Optional?
        - Not all IDs exist in the system (invalid or deleted categories)
        - None is a clear signal that "category not found"
        - Caller can check: if category is None: handle_not_found()

        Implementation notes for adapters:
        - Return None if category doesn't exist (don't raise exception)
        - ID comparison should be case-sensitive
        - Return a full MenuCategory object with all fields populated
        """
        pass  # Abstract method - no implementation here

    # Note: In a full implementation, we might also have:
    # - save_category(category: MenuCategory) -> None
    # - delete_category(category_id: str) -> None
    # - find_categories_by_name(name: str) -> List[MenuCategory]
    # But we keep it simple for Module 2 (read-only operations)
