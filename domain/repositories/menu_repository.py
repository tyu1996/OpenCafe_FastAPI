# Import ABC (Abstract Base Class) - allows us to define interfaces
# An interface defines WHAT methods must exist, but not HOW they work
from abc import ABC, abstractmethod

# Import typing for type hints
# List means "a list of items", Optional means "can be None"
from typing import List, Optional

# Import our MenuItem entity
# This is okay - domain entities can import other domain entities
from domain.entities.menu import MenuItem


class MenuRepository(ABC):
    """
    MenuRepository is a PORT (interface) in the Ports & Adapters pattern.

    WHAT IS A PORT?
    - A port defines WHAT operations we need, but not HOW to do them
    - It's like a USB port on your laptop - defines the shape and rules
    - Different adapters (cables) can plug into the same port

    WHY USE PORTS?
    - Keeps our business logic independent of implementation details
    - Easy to swap implementations (in-memory -> database -> API)
    - Makes testing easy - use a fake adapter in tests
    - Follows Dependency Inversion Principle (depend on abstractions, not concretions)

    WHO IMPLEMENTS THIS?
    - Infrastructure layer creates ADAPTERS that implement this port
    - Examples: InMemoryMenuRepository, SQLAlchemyMenuRepository, etc.

    Real-world analogy:
    - This interface is like a restaurant's ordering system specification
    - Different chefs (adapters) can follow the same specification
    - The front of house (application layer) doesn't care which chef is cooking
    """

    @abstractmethod  # This decorator marks the method as "must be implemented by subclasses"
    def list_all_items(self) -> List[MenuItem]:
        """
        Return all menu items in the system.

        Returns:
            List[MenuItem]: List of all MenuItem objects, could be empty

        Why this exists:
        - Core business operation: viewing the entire menu
        - No parameters because we want EVERYTHING
        - Different adapters might get items from memory, database, or API
        """
        pass  # Abstract methods have no implementation - subclasses provide the real code

    @abstractmethod
    def get_item_by_id(self, item_id: str) -> Optional[MenuItem]:
        """
        Find and return a single menu item by its unique ID.

        Args:
            item_id (str): The unique identifier for the menu item

        Returns:
            Optional[MenuItem]: The menu item if found, None if not found

        Why Optional?
        - The item might not exist (maybe deleted or wrong ID)
        - Optional[MenuItem] means "might be MenuItem, might be None"
        - Better than raising an exception - not finding something isn't an error
        - Calling code can check: if item is None: handle_not_found()

        Why this exists:
        - Common operation: get details of one specific item
        - Used when customer clicks on an item for more info
        - Used when building orders (need to look up item by ID)
        """
        pass
