# Import pytest for testing framework
import pytest

# Import datetime and Decimal for test data
from datetime import datetime
from decimal import Decimal

# Import the entities we're testing
from domain.entities.order import Order, OrderItem, OrderStatus


class TestOrderStatus:
    """Tests for OrderStatus enum"""

    def test_order_status_values(self):
        """Test that OrderStatus has all expected values"""
        assert OrderStatus.PENDING.value == "pending"
        assert OrderStatus.CONFIRMED.value == "confirmed"
        assert OrderStatus.PREPARING.value == "preparing"
        assert OrderStatus.READY.value == "ready"
        assert OrderStatus.COMPLETED.value == "completed"


class TestOrderItem:
    """Tests for OrderItem value object"""

    def test_create_valid_order_item(self):
        """Test creating a valid OrderItem"""
        # Arrange & Act
        item = OrderItem(
            menu_item_id="item-001",
            menu_item_name="Espresso",
            unit_price=Decimal("2.50"),
            quantity=2,
        )

        # Assert
        assert item.menu_item_id == "item-001"
        assert item.menu_item_name == "Espresso"
        assert item.unit_price == Decimal("2.50")
        assert item.quantity == 2

    def test_order_item_subtotal_calculation(self):
        """Test that subtotal is calculated correctly"""
        # Arrange
        item = OrderItem(
            menu_item_id="item-001",
            menu_item_name="Espresso",
            unit_price=Decimal("2.50"),
            quantity=3,
        )

        # Act
        subtotal = item.subtotal

        # Assert
        # 2.50 * 3 = 7.50
        assert subtotal == Decimal("7.50")

    def test_order_item_zero_quantity_fails(self):
        """Test that OrderItem with quantity 0 fails validation"""
        # Act & Assert
        with pytest.raises(ValueError, match="quantity must be greater than zero"):
            OrderItem(
                menu_item_id="item-001",
                menu_item_name="Espresso",
                unit_price=Decimal("2.50"),
                quantity=0,  # Invalid!
            )

    def test_order_item_negative_quantity_fails(self):
        """Test that OrderItem with negative quantity fails validation"""
        # Act & Assert
        with pytest.raises(ValueError, match="quantity must be greater than zero"):
            OrderItem(
                menu_item_id="item-001",
                menu_item_name="Espresso",
                unit_price=Decimal("2.50"),
                quantity=-1,  # Invalid!
            )

    def test_order_item_negative_price_fails(self):
        """Test that OrderItem with negative price fails validation"""
        # Act & Assert
        with pytest.raises(ValueError, match="price cannot be negative"):
            OrderItem(
                menu_item_id="item-001",
                menu_item_name="Espresso",
                unit_price=Decimal("-2.50"),  # Invalid!
                quantity=2,
            )

    def test_order_item_empty_name_fails(self):
        """Test that OrderItem with empty name fails validation"""
        # Act & Assert
        with pytest.raises(ValueError, match="name cannot be empty"):
            OrderItem(
                menu_item_id="item-001",
                menu_item_name="",  # Invalid!
                unit_price=Decimal("2.50"),
                quantity=2,
            )

    def test_order_item_is_immutable(self):
        """Test that OrderItem is immutable (frozen dataclass)"""
        # Arrange
        item = OrderItem(
            menu_item_id="item-001",
            menu_item_name="Espresso",
            unit_price=Decimal("2.50"),
            quantity=2,
        )

        # Act & Assert - trying to modify should raise error
        with pytest.raises(Exception):  # FrozenInstanceError
            item.quantity = 3


class TestOrder:
    """Tests for Order aggregate root"""

    def test_create_valid_order(self):
        """Test creating a valid Order"""
        # Arrange
        items = [
            OrderItem(
                menu_item_id="item-001",
                menu_item_name="Espresso",
                unit_price=Decimal("2.50"),
                quantity=2,
            )
        ]

        # Act
        order = Order(
            id="order-001",
            table_id="table-001",
            items=items,
            status=OrderStatus.PENDING,
            created_at=datetime(2024, 1, 15, 14, 30),
        )

        # Assert
        assert order.id == "order-001"
        assert order.table_id == "table-001"
        assert len(order.items) == 1
        assert order.status == OrderStatus.PENDING
        assert order.created_at == datetime(2024, 1, 15, 14, 30)

    def test_order_total_calculation_single_item(self):
        """Test that order total is calculated correctly with one item"""
        # Arrange
        items = [
            OrderItem(
                menu_item_id="item-001",
                menu_item_name="Espresso",
                unit_price=Decimal("2.50"),
                quantity=2,
            )
        ]
        order = Order(
            id="order-001",
            table_id="table-001",
            items=items,
            status=OrderStatus.PENDING,
            created_at=datetime.utcnow(),
        )

        # Act
        total = order.total

        # Assert
        # 2.50 * 2 = 5.00
        assert total == Decimal("5.00")

    def test_order_total_calculation_multiple_items(self):
        """Test that order total is calculated correctly with multiple items"""
        # Arrange
        items = [
            OrderItem(
                menu_item_id="item-001",
                menu_item_name="Espresso",
                unit_price=Decimal("2.50"),
                quantity=2,
            ),
            OrderItem(
                menu_item_id="item-002",
                menu_item_name="Croissant",
                unit_price=Decimal("3.50"),
                quantity=1,
            ),
        ]
        order = Order(
            id="order-001",
            table_id="table-001",
            items=items,
            status=OrderStatus.PENDING,
            created_at=datetime.utcnow(),
        )

        # Act
        total = order.total

        # Assert
        # (2.50 * 2) + (3.50 * 1) = 5.00 + 3.50 = 8.50
        assert total == Decimal("8.50")

    def test_order_empty_items_fails(self):
        """Test that Order with no items fails validation"""
        # Act & Assert
        with pytest.raises(ValueError, match="must contain at least one item"):
            Order(
                id="order-001",
                table_id="table-001",
                items=[],  # Invalid - empty list!
                status=OrderStatus.PENDING,
                created_at=datetime.utcnow(),
            )

    def test_order_status_is_mutable(self):
        """Test that Order status can be changed (Order is mutable)"""
        # Arrange
        items = [
            OrderItem(
                menu_item_id="item-001",
                menu_item_name="Espresso",
                unit_price=Decimal("2.50"),
                quantity=2,
            )
        ]
        order = Order(
            id="order-001",
            table_id="table-001",
            items=items,
            status=OrderStatus.PENDING,
            created_at=datetime.utcnow(),
        )

        # Act - change status (this should work because Order is NOT frozen)
        order.status = OrderStatus.CONFIRMED

        # Assert
        assert order.status == OrderStatus.CONFIRMED

    def test_order_with_different_statuses(self):
        """Test that Order can be created with different statuses"""
        items = [
            OrderItem(
                menu_item_id="item-001",
                menu_item_name="Espresso",
                unit_price=Decimal("2.50"),
                quantity=1,
            )
        ]

        # Test each status
        for status in [
            OrderStatus.PENDING,
            OrderStatus.CONFIRMED,
            OrderStatus.PREPARING,
            OrderStatus.READY,
            OrderStatus.COMPLETED,
        ]:
            order = Order(
                id=f"order-{status.value}",
                table_id="table-001",
                items=items,
                status=status,
                created_at=datetime.utcnow(),
            )
            assert order.status == status
