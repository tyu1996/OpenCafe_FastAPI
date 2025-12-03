# Import testing utilities
import pytest

# Import Decimal for menu item prices
from decimal import Decimal

# Import the domain entities and ports we'll use
from domain.entities.menu import MenuItem
from domain.repositories.menu_repository import MenuRepository

# Import the use case we're testing (System Under Test)
from application.use_cases.list_menu_items import ListMenuItems

# Import List and Optional for type hints
from typing import List, Optional


class FakeMenuRepository(MenuRepository):
    """
    Fake (test double) implementation of MenuRepository.

    WHAT IS A FAKE?
    - A simplified working implementation used only for testing
    - Different from a mock: a fake has real behavior, a mock just records calls
    - Different from the real thing: simpler, in-memory, no side effects

    WHY USE A FAKE?
    - Tests run fast (no database, no network)
    - Tests are isolated (don't affect other tests)
    - Tests are deterministic (same input = same output, always)
    - We control the data (can test edge cases easily)

    This is a KEY BENEFIT of the ports & adapters pattern:
    - The use case depends on an interface (MenuRepository)
    - We can easily swap in a fake for testing
    - No need for complex mocking frameworks
    """

    def __init__(self, items: List[MenuItem]):
        """
        Initialize the fake repository with a list of items.

        Args:
            items: List of MenuItem objects to store in memory
                   We pass these in so each test can control what data exists
        """
        # Store items in a dictionary for quick lookup by ID
        # Dictionary comprehension: {key: value for item in items}
        self._items = {item.id: item for item in items}

    def list_all_items(self) -> List[MenuItem]:
        """Return all items as a list."""
        # Convert dictionary values back to a list
        # list(dict.values()) gives us all the values
        return list(self._items.values())

    def get_item_by_id(self, item_id: str) -> Optional[MenuItem]:
        """Return item by ID or None if not found."""
        # Dictionary .get() returns None if key doesn't exist
        # This is safer than self._items[item_id] which would raise KeyError
        return self._items.get(item_id)


class TestListMenuItems:
    """
    Test suite for ListMenuItems use case.

    These are UNIT TESTS for application layer:
    - Test the use case in isolation
    - Use fake repository (no real database)
    - Fast execution (< 1 second for all tests)
    - No FastAPI dependencies

    This demonstrates a key architecture benefit:
    - We can test business logic WITHOUT starting a web server
    - We can test WITHOUT a database
    - Tests are fast and reliable
    """

    def test_list_all_items(self):
        """
        Test listing all items when only_available is False.

        This tests the basic operation: get everything from repository.
        """
        # Arrange: Create test data
        # Build a list of MenuItem objects to use in our test
        items = [
            MenuItem(
                id="item-001",
                name="Espresso",
                description="Strong Italian coffee",
                price=Decimal("2.50"),
                category="coffee",
                available=True
            ),
            MenuItem(
                id="item-002",
                name="Cappuccino",
                description="Espresso with steamed milk foam",
                price=Decimal("3.50"),
                category="coffee",
                available=True
            ),
            MenuItem(
                id="item-003",
                name="Croissant",
                description="Buttery French pastry",
                price=Decimal("2.75"),
                category="pastry",
                available=False  # This one is NOT available
            )
        ]

        # Create fake repository with our test data
        fake_repo = FakeMenuRepository(items)

        # Create use case with the fake repository (dependency injection)
        use_case = ListMenuItems(menu_repository=fake_repo)

        # Act: Execute the use case with only_available=False (get everything)
        result = use_case.execute(only_available=False)

        # Assert: Should return all 3 items (including unavailable one)
        assert len(result) == 3, "Should return all items when only_available=False"
        assert result[0].name == "Espresso", "First item should be Espresso"
        assert result[1].name == "Cappuccino", "Second item should be Cappuccino"
        assert result[2].name == "Croissant", "Third item should be Croissant"

    def test_list_only_available_items(self):
        """
        Test filtering to only available items (default behavior).

        This tests the filtering logic: only_available=True.
        """
        # Arrange: Create mix of available and unavailable items
        items = [
            MenuItem(
                id="item-001",
                name="Espresso",
                description="Strong Italian coffee",
                price=Decimal("2.50"),
                category="coffee",
                available=True  # Available
            ),
            MenuItem(
                id="item-002",
                name="Latte",
                description="Espresso with steamed milk",
                price=Decimal("4.00"),
                category="coffee",
                available=False  # NOT available (out of stock)
            ),
            MenuItem(
                id="item-003",
                name="Croissant",
                description="Buttery French pastry",
                price=Decimal("2.75"),
                category="pastry",
                available=True  # Available
            )
        ]

        fake_repo = FakeMenuRepository(items)
        use_case = ListMenuItems(menu_repository=fake_repo)

        # Act: Execute with only_available=True (this is the default)
        result = use_case.execute(only_available=True)

        # Assert: Should return only the 2 available items
        assert len(result) == 2, "Should return only available items"
        # Check that unavailable item (Latte) is NOT in the result
        result_names = [item.name for item in result]
        assert "Espresso" in result_names, "Espresso should be included (available=True)"
        assert "Croissant" in result_names, "Croissant should be included (available=True)"
        assert "Latte" not in result_names, "Latte should be excluded (available=False)"

    def test_list_with_default_only_available(self):
        """
        Test that only_available defaults to True.

        This tests the default parameter value.
        """
        # Arrange: One available, one unavailable
        items = [
            MenuItem(
                id="item-001",
                name="Espresso",
                description="Strong Italian coffee",
                price=Decimal("2.50"),
                category="coffee",
                available=True
            ),
            MenuItem(
                id="item-002",
                name="Latte",
                description="Out of stock",
                price=Decimal("4.00"),
                category="coffee",
                available=False
            )
        ]

        fake_repo = FakeMenuRepository(items)
        use_case = ListMenuItems(menu_repository=fake_repo)

        # Act: Call execute WITHOUT specifying only_available
        # Should default to True
        result = use_case.execute()  # No argument = uses default

        # Assert: Should return only available item (default behavior)
        assert len(result) == 1, "Should filter to available items by default"
        assert result[0].name == "Espresso", "Should return the available item"

    def test_list_empty_repository(self):
        """
        Test listing items when repository is empty.

        This tests an edge case: what happens when there's no data?
        Good code handles empty results gracefully.
        """
        # Arrange: Create empty repository
        empty_items = []  # No items at all
        fake_repo = FakeMenuRepository(empty_items)
        use_case = ListMenuItems(menu_repository=fake_repo)

        # Act: Execute the use case
        result = use_case.execute()

        # Assert: Should return empty list (not None, not error)
        assert result == [], "Should return empty list when repository is empty"
        assert len(result) == 0, "Result should have length 0"
        assert isinstance(result, list), "Should return a list (even if empty)"

    def test_list_all_unavailable_items(self):
        """
        Test filtering when ALL items are unavailable.

        Edge case: every item has available=False.
        """
        # Arrange: Create items that are all unavailable
        items = [
            MenuItem(
                id="item-001",
                name="Espresso",
                description="Out of stock",
                price=Decimal("2.50"),
                category="coffee",
                available=False  # Unavailable
            ),
            MenuItem(
                id="item-002",
                name="Latte",
                description="Out of stock",
                price=Decimal("4.00"),
                category="coffee",
                available=False  # Unavailable
            )
        ]

        fake_repo = FakeMenuRepository(items)
        use_case = ListMenuItems(menu_repository=fake_repo)

        # Act: Execute with only_available=True
        result = use_case.execute(only_available=True)

        # Assert: Should return empty list (all items filtered out)
        assert result == [], "Should return empty list when all items are unavailable"

    def test_repository_is_injected_via_constructor(self):
        """
        Test that we can inject different repository implementations.

        This tests the dependency injection pattern.
        We create a DIFFERENT fake repository and verify it's used.
        """
        # Arrange: Create repository with specific test data
        items = [
            MenuItem(
                id="test-001",
                name="Test Item",
                description="For testing DI",
                price=Decimal("1.00"),
                category="test",
                available=True
            )
        ]
        fake_repo = FakeMenuRepository(items)

        # Act: Inject our repository into the use case
        use_case = ListMenuItems(menu_repository=fake_repo)
        result = use_case.execute()

        # Assert: Use case should use our injected repository
        assert len(result) == 1, "Should use the injected repository"
        assert result[0].name == "Test Item", "Should return data from injected repository"

        # Key insight: We can swap the repository implementation
        # without changing the use case code at all!
        # This is the power of dependency injection + interfaces
