# Import pytest for testing
import pytest

# Import required types
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

# Import entities
from domain.entities.menu import MenuItem
from domain.entities.table import Table
from domain.entities.order import Order, OrderStatus

# Import repository interfaces
from domain.repositories.menu_repository import MenuRepository
from domain.repositories.table_repository import TableRepository
from domain.repositories.order_repository import OrderRepository

# Import the use case we're testing
from application.use_cases.place_order import PlaceOrder

# Import the DTO
from interfaces.api.schemas.orders import CreateOrderRequest, OrderItemInput


# ===== Fake Repositories for Testing =====
# These are simple in-memory implementations that we use ONLY for testing
# They let us test the use case without a real database


class FakeMenuRepository(MenuRepository):
    """Fake menu repository for testing"""

    def __init__(self, items: List[MenuItem]):
        self._items = {item.id: item for item in items}

    def list_all_items(self) -> List[MenuItem]:
        return list(self._items.values())

    def get_item_by_id(self, item_id: str) -> Optional[MenuItem]:
        return self._items.get(item_id)

    def list_items(
        self,
        only_available: bool = True,
        category_id: str | None = None,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[MenuItem]:
        """List items with filtering (MODULE 4)."""
        items = list(self._items.values())
        if only_available:
            items = [item for item in items if item.available]
        if category_id:
            items = [item for item in items if item.category == category_id]
        if search:
            search_lower = search.lower()
            items = [
                item for item in items
                if search_lower in item.name.lower() or search_lower in item.description.lower()
            ]
        return items[offset:offset + limit]


class FakeTableRepository(TableRepository):
    """Fake table repository for testing"""

    def __init__(self, tables: List[Table]):
        self._tables = {table.id: table for table in tables}

    def list_all_tables(self) -> List[Table]:
        return list(self._tables.values())

    def list_tables(self, area: str | None = None) -> List[Table]:
        """List tables with optional area filter (MODULE 4)."""
        tables = list(self._tables.values())
        if area is not None:
            area_lower = area.lower()
            tables = [t for t in tables if t.location.lower() == area_lower]
        return tables

    def get_table_by_id(self, table_id: str) -> Optional[Table]:
        return self._tables.get(table_id)


class FakeOrderRepository(OrderRepository):
    """Fake order repository for testing"""

    def __init__(self):
        self._orders = {}

    def save_order(self, order: Order) -> None:
        self._orders[order.id] = order

    def get_order_by_id(self, order_id: str) -> Optional[Order]:
        return self._orders.get(order_id)

    def get_open_order_for_table(self, table_id: str) -> Optional[Order]:
        """Get any open order for a table (MODULE 5)."""
        # Find any order for this table with PENDING or CONFIRMED status
        for order in self._orders.values():
            if (order.table_id == table_id and
                order.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]):
                return order
        return None


# ===== Test Fixtures =====
# Fixtures are reusable test data that pytest provides to test functions


@pytest.fixture
def sample_menu_items():
    """Fixture that provides sample menu items for tests"""
    return [
        MenuItem(
            id="item-001",
            name="Espresso",
            description="Strong Italian coffee",
            price=Decimal("2.50"),
            category="coffee",
            available=True,
        ),
        MenuItem(
            id="item-002",
            name="Cappuccino",
            description="Espresso with steamed milk",
            price=Decimal("3.50"),
            category="coffee",
            available=True,
        ),
        MenuItem(
            id="item-003",
            name="Croissant",
            description="Buttery French pastry",
            price=Decimal("3.00"),
            category="pastry",
            available=True,
        ),
    ]


@pytest.fixture
def sample_tables():
    """Fixture that provides sample tables for tests"""
    return [
        Table(id="table-001", number=1, capacity=2, location="window"),
        Table(id="table-002", number=2, capacity=4, location="main-room"),
    ]


@pytest.fixture
def place_order_use_case(sample_menu_items, sample_tables):
    """Fixture that provides a configured PlaceOrder use case"""
    # Create fake repositories with test data
    menu_repo = FakeMenuRepository(sample_menu_items)
    table_repo = FakeTableRepository(sample_tables)
    order_repo = FakeOrderRepository()

    # Create and return use case with fakes injected
    return PlaceOrder(
        order_repository=order_repo,
        table_repository=table_repo,
        menu_repository=menu_repo,
    )


# ===== Tests =====


class TestPlaceOrder:
    """Tests for PlaceOrder use case"""

    def test_place_order_success_single_item(self, place_order_use_case):
        """Test successfully placing an order with one item"""
        # Arrange - create request DTO
        request = CreateOrderRequest(
            table_id="table-001",
            items=[
                OrderItemInput(item_id="item-001", quantity=2),  # 2 Espressos
            ],
        )

        # Act - execute use case
        order = place_order_use_case.execute(request)

        # Assert - verify order was created correctly
        assert order is not None
        assert order.table_id == "table-001"
        assert order.status == OrderStatus.PENDING
        assert len(order.items) == 1

        # Verify OrderItem has snapshot data
        order_item = order.items[0]
        assert order_item.menu_item_id == "item-001"
        assert order_item.menu_item_name == "Espresso"  # Snapshot!
        assert order_item.unit_price == Decimal("2.50")  # Snapshot!
        assert order_item.quantity == 2

        # Verify subtotal and total
        assert order_item.subtotal == Decimal("5.00")  # 2.50 * 2
        assert order.total == Decimal("5.00")

    def test_place_order_success_multiple_items(self, place_order_use_case):
        """Test successfully placing an order with multiple items"""
        # Arrange
        request = CreateOrderRequest(
            table_id="table-002",
            items=[
                OrderItemInput(item_id="item-001", quantity=2),  # 2 Espressos
                OrderItemInput(item_id="item-003", quantity=1),  # 1 Croissant
            ],
        )

        # Act
        order = place_order_use_case.execute(request)

        # Assert
        assert order is not None
        assert order.table_id == "table-002"
        assert len(order.items) == 2

        # Verify first item
        item1 = order.items[0]
        assert item1.menu_item_name == "Espresso"
        assert item1.unit_price == Decimal("2.50")
        assert item1.quantity == 2
        assert item1.subtotal == Decimal("5.00")

        # Verify second item
        item2 = order.items[1]
        assert item2.menu_item_name == "Croissant"
        assert item2.unit_price == Decimal("3.00")
        assert item2.quantity == 1
        assert item2.subtotal == Decimal("3.00")

        # Verify total
        assert order.total == Decimal("8.00")  # 5.00 + 3.00

    def test_place_order_table_not_found(self, place_order_use_case):
        """Test that placing order for non-existent table fails"""
        # Arrange
        request = CreateOrderRequest(
            table_id="table-999",  # Doesn't exist!
            items=[
                OrderItemInput(item_id="item-001", quantity=1),
            ],
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Table.*not found"):
            place_order_use_case.execute(request)

    def test_place_order_menu_item_not_found(self, place_order_use_case):
        """Test that placing order with non-existent menu item fails"""
        # Arrange
        request = CreateOrderRequest(
            table_id="table-001",
            items=[
                OrderItemInput(item_id="item-999", quantity=1),  # Doesn't exist!
            ],
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Menu item.*not found"):
            place_order_use_case.execute(request)

    def test_place_order_creates_unique_id(self, place_order_use_case):
        """Test that each order gets a unique ID"""
        # Arrange - MODULE 5: Use different tables since same table can't have 2 open orders
        request1 = CreateOrderRequest(
            table_id="table-001",
            items=[OrderItemInput(item_id="item-001", quantity=1)],
        )
        request2 = CreateOrderRequest(
            table_id="table-002",  # Different table!
            items=[OrderItemInput(item_id="item-001", quantity=1)],
        )

        # Act - create two orders for different tables
        order1 = place_order_use_case.execute(request1)
        order2 = place_order_use_case.execute(request2)

        # Assert - IDs should be different
        assert order1.id != order2.id

    def test_place_order_sets_created_at(self, place_order_use_case):
        """Test that order has created_at timestamp"""
        # Arrange
        request = CreateOrderRequest(
            table_id="table-001",
            items=[OrderItemInput(item_id="item-001", quantity=1)],
        )

        # Act
        before = datetime.now(timezone.utc)
        order = place_order_use_case.execute(request)
        after = datetime.now(timezone.utc)

        # Assert - created_at should be between before and after
        assert order.created_at is not None
        assert before <= order.created_at <= after

    def test_place_order_snapshots_price(self, sample_menu_items, sample_tables):
        """Test that order captures current price (snapshot pattern)"""
        # Arrange - create repositories
        menu_repo = FakeMenuRepository(sample_menu_items)
        table_repo = FakeTableRepository(sample_tables)
        order_repo = FakeOrderRepository()
        use_case = PlaceOrder(order_repo, table_repo, menu_repo)

        request1 = CreateOrderRequest(
            table_id="table-001",
            items=[OrderItemInput(item_id="item-001", quantity=1)],
        )

        # Act - place first order
        order = use_case.execute(request1)

        # Verify snapshot price
        assert order.items[0].unit_price == Decimal("2.50")

        # Now simulate menu price change
        # (In real system, this would update the database)
        sample_menu_items[0] = MenuItem(
            id="item-001",
            name="Espresso",
            description="Strong Italian coffee",
            price=Decimal("3.00"),  # Price increased!
            category="coffee",
            available=True,
        )
        menu_repo = FakeMenuRepository(sample_menu_items)
        use_case2 = PlaceOrder(order_repo, table_repo, menu_repo)

        # MODULE 5: Place order for different table (same table can't have 2 open orders)
        request2 = CreateOrderRequest(
            table_id="table-002",  # Different table!
            items=[OrderItemInput(item_id="item-001", quantity=1)],
        )
        order2 = use_case2.execute(request2)

        # Assert - first order still has old price (snapshot!)
        assert order.items[0].unit_price == Decimal("2.50")
        # But new order has new price
        assert order2.items[0].unit_price == Decimal("3.00")
