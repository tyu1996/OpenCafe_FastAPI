# Import pytest - our testing framework
import pytest

# Import Decimal for testing money values
from decimal import Decimal

# Import the MenuItem entity we want to test
# This is the SYSTEM UNDER TEST (SUT)
from domain.entities.menu import MenuItem


class TestMenuItem:
    """
    Test suite for MenuItem domain entity.

    Why test domain entities?
    - They contain critical business rules
    - Bugs here affect everything built on top
    - These tests are fast (no database, no API)
    - They document how the entity should behave

    Test structure follows AAA pattern:
    - Arrange: Set up test data
    - Act: Do the thing you're testing
    - Assert: Check the result is correct
    """

    def test_create_valid_menu_item(self):
        """
        Test that we can create a MenuItem with valid data.

        This is the "happy path" test - everything works correctly.
        """
        # Arrange: Prepare test data
        # Use clear, realistic example data
        item_id = "item-001"
        name = "Espresso"
        description = "Strong Italian coffee"
        price = Decimal("2.50")  # Use Decimal for money!
        category = "coffee"
        available = True

        # Act: Create the MenuItem
        # This is what we're testing
        item = MenuItem(
            id=item_id,
            name=name,
            description=description,
            price=price,
            category=category,
            available=available
        )

        # Assert: Check all attributes are set correctly
        # Each assertion checks one specific thing
        assert item.id == item_id, "ID should match what we passed in"
        assert item.name == name, "Name should match what we passed in"
        assert item.description == description, "Description should match"
        assert item.price == price, "Price should match"
        assert item.category == category, "Category should match"
        assert item.available == available, "Available flag should match"

    def test_create_menu_item_with_default_available(self):
        """
        Test that 'available' defaults to True when not specified.

        This tests the default value behavior of the dataclass.
        """
        # Arrange & Act: Create MenuItem without specifying 'available'
        item = MenuItem(
            id="item-002",
            name="Cappuccino",
            description="Espresso with steamed milk foam",
            price=Decimal("3.50"),
            category="coffee"
            # Note: available is not specified
        )

        # Assert: Should default to True
        assert item.available is True, "available should default to True"

    def test_negative_price_raises_value_error(self):
        """
        Test that creating a MenuItem with negative price raises ValueError.

        This tests our business rule: prices must be non-negative.
        We use pytest.raises to assert that an exception is raised.
        """
        # Arrange: Prepare data with invalid (negative) price
        invalid_price = Decimal("-5.00")  # This is invalid!

        # Act & Assert: Expect ValueError to be raised
        # pytest.raises is a context manager that catches the exception
        with pytest.raises(ValueError, match="Price cannot be negative"):
            # This code should raise ValueError
            MenuItem(
                id="item-003",
                name="Invalid Item",
                description="This should fail",
                price=invalid_price,  # This triggers the validation error
                category="coffee"
            )

        # If we get here, the test passed (ValueError was raised as expected)

    def test_empty_name_raises_value_error(self):
        """
        Test that creating a MenuItem with empty name raises ValueError.

        This tests our business rule: names cannot be empty.
        """
        # Arrange: Prepare data with invalid (empty) name
        empty_name = ""  # Invalid!

        # Act & Assert: Expect ValueError
        with pytest.raises(ValueError, match="Name cannot be empty"):
            MenuItem(
                id="item-004",
                name=empty_name,  # This triggers the validation error
                description="This should fail",
                price=Decimal("2.50"),
                category="coffee"
            )

    def test_whitespace_only_name_raises_value_error(self):
        """
        Test that a name with only whitespace raises ValueError.

        This tests edge case: name="   " (just spaces) should fail.
        Our validation uses .strip() so "   " becomes "" which fails.
        """
        # Arrange: Name with only spaces
        whitespace_name = "   "  # Invalid! (empty after stripping)

        # Act & Assert: Expect ValueError
        with pytest.raises(ValueError, match="Name cannot be empty"):
            MenuItem(
                id="item-005",
                name=whitespace_name,  # This should fail validation
                description="This should fail",
                price=Decimal("2.50"),
                category="coffee"
            )

    def test_menu_item_is_immutable(self):
        """
        Test that MenuItem is immutable (cannot be modified after creation).

        We used frozen=True in the dataclass decorator, which makes it immutable.
        This is important for domain entities - they should be values, not mutable objects.

        Why immutability?
        - Prevents bugs from unexpected changes
        - Makes objects safe to share
        - Aligns with functional programming principles
        """
        # Arrange & Act: Create a MenuItem
        item = MenuItem(
            id="item-006",
            name="Croissant",
            description="Buttery French pastry",
            price=Decimal("2.75"),
            category="pastry"
        )

        # Assert: Trying to modify an attribute should raise an error
        # FrozenInstanceError is raised when you try to modify a frozen dataclass
        with pytest.raises(Exception):  # Will raise FrozenInstanceError (subclass of Exception)
            # Attempting to change the price should fail
            item.price = Decimal("3.00")  # This should raise FrozenInstanceError

        # The item remains unchanged
        assert item.price == Decimal("2.75"), "Price should still be original value"

    def test_zero_price_is_allowed(self):
        """
        Test that price of zero is valid.

        This is a boundary test: 0 is on the edge between valid and invalid.
        Our rule is "price < 0" is invalid, so 0 should be valid.

        This might represent a free sample or promotional item.
        """
        # Arrange & Act: Create item with price of zero
        item = MenuItem(
            id="item-007",
            name="Free Sample",
            description="Promotional item",
            price=Decimal("0.00"),  # Zero is valid
            category="promo"
        )

        # Assert: No error should be raised, and price should be 0
        assert item.price == Decimal("0.00"), "Zero price should be allowed"
