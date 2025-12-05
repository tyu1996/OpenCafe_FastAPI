# Import datetime for timestamps
from datetime import datetime

# Import Decimal for precise money calculations
from decimal import Decimal

# Import uuid for generating unique IDs
import uuid

# Import the domain entities we'll work with
from domain.entities.order import Order, OrderItem, OrderStatus

# Import repository interfaces (ports)
from domain.repositories.menu_repository import MenuRepository
from domain.repositories.order_repository import OrderRepository
from domain.repositories.table_repository import TableRepository

# Import the input DTO (API request model)
from interfaces.api.schemas.orders import CreateOrderRequest


class PlaceOrder:
    """
    Use case for placing a new order.

    This is the MOST IMPORTANT USE CASE in Module 2!
    It demonstrates the complete flow of Clean Architecture:
    1. Receive DTO from API layer (CreateOrderRequest)
    2. Validate business rules (table exists, items exist)
    3. Create domain entities (Order with OrderItems)
    4. Save via repository
    5. Return domain entity (router converts to OrderResponse DTO)

    This use case showcases:
    - DTO → Entity conversion
    - Multi-repository coordination
    - Business validation
    - Snapshot pattern (capturing prices at order time)
    - Aggregate creation (Order with OrderItems)

    Real-world analogy: Think of this as the kitchen receiving an order ticket.
    1. Waiter writes order on ticket (CreateOrderRequest DTO)
    2. Kitchen validates table exists and items are on menu
    3. Kitchen creates official order ticket with prices (Order entity)
    4. Ticket is pinned to board (save to repository)
    5. Kitchen returns ticket number (Order entity returned)

    DEPENDENCIES (3 repositories):
    - OrderRepository: save the new order
    - TableRepository: validate table exists
    - MenuRepository: look up item details and prices

    Why so many dependencies?
    - Placing an order touches multiple domain concepts
    - Each repository is responsible for one entity type
    - This is normal for orchestrating use cases

    BUSINESS RULES ENFORCED:
    1. Table must exist (can't order for non-existent table)
    2. All menu items must exist (can't order items not on menu)
    3. Order must have at least one item (checked by Order entity)
    4. Quantities must be positive (checked by OrderItem entity)
    5. Prices are captured at order time (snapshot pattern)
    """

    def __init__(
        self,
        order_repository: OrderRepository,
        table_repository: TableRepository,
        menu_repository: MenuRepository,
    ):
        """
        Initialize the use case with its dependencies.

        Args:
            order_repository: For saving the new order
            table_repository: For validating table exists
            menu_repository: For looking up menu item details

        DEPENDENCY INJECTION:
        All three repositories are injected (not created inside).
        This makes testing easy: pass fake repositories.
        """
        # Store repositories for later use
        self._order_repository = order_repository
        self._table_repository = table_repository
        self._menu_repository = menu_repository

    def execute(self, request: CreateOrderRequest) -> Order:
        """
        Execute the use case: place a new order.

        This is where the main business logic happens.
        This method coordinates multiple repositories and creates the order.

        Args:
            request (CreateOrderRequest): DTO with order data from API
                Contains: table_id, items (list of {item_id, quantity})

        Returns:
            Order: The created domain entity
                Router will convert this to OrderResponse DTO for API response

        Raises:
            ValueError: If validation fails (table not found, item not found)

        Algorithm (6 steps):
        1. Validate table exists
        2. Look up each menu item and validate it exists
        3. Create OrderItem objects with snapshot data (name, price)
        4. Generate order ID and timestamp
        5. Create Order entity (triggers domain validation)
        6. Save order and return it

        This is the HEART of Module 2's learning!
        """

        # STEP 1: Validate table exists
        # We can't place an order for a non-existent table
        # This is BUSINESS VALIDATION (not just format validation)
        table = self._table_repository.get_table_by_id(request.table_id)

        # If table not found, raise clear error
        # Caller (router) will convert this to 404 or 400 response
        if table is None:
            raise ValueError(f"Table with ID '{request.table_id}' not found")

        # STEP 2: Look up menu items and create OrderItem objects
        # This is the most complex part: converting from DTO to domain entities
        order_items = []  # Will hold OrderItem domain entities

        # Loop through each item in the request
        for item_input in request.items:
            # Look up the menu item to get its current details
            # We need the name and price for the snapshot
            menu_item = self._menu_repository.get_item_by_id(item_input.item_id)

            # If menu item not found, raise clear error
            if menu_item is None:
                raise ValueError(f"Menu item with ID '{item_input.item_id}' not found")

            # KEY TEACHING POINT: SNAPSHOT PATTERN
            # We capture name and price NOW, at order time
            # Even if menu changes later, this order shows original values
            # This is DENORMALIZATION - intentional data duplication

            # Create OrderItem (value object, immutable)
            # Notice: we pass menu_item data (name, price) to create the snapshot
            order_item = OrderItem(
                menu_item_id=item_input.item_id,  # Reference to menu item
                menu_item_name=menu_item.name,  # SNAPSHOT: current name
                unit_price=menu_item.price,  # SNAPSHOT: current price
                quantity=item_input.quantity,  # From client request
            )

            # OrderItem constructor validates:
            # - quantity > 0
            # - unit_price >= 0
            # - name is not empty
            # If validation fails, ValueError is raised

            # Add to list
            order_items.append(order_item)

        # Now we have all OrderItems with snapshot data!

        # STEP 3: Generate order ID
        # Use UUID to generate unique identifier
        # str(uuid.uuid4()) creates string like "123e4567-e89b-12d3-a456-426614174000"
        order_id = str(uuid.uuid4())

        # STEP 4: Get current timestamp
        # datetime.utcnow() returns current UTC time
        # Use UTC (not local time) for consistency across timezones
        created_at = datetime.utcnow()

        # STEP 5: Create Order entity (aggregate root)
        # This is where domain validation happens!
        # Order constructor will validate:
        # - items list is not empty
        # - All other business invariants
        order = Order(
            id=order_id,  # Generated UUID
            table_id=request.table_id,  # From request
            items=order_items,  # List of OrderItem entities we built
            status=OrderStatus.PENDING,  # New orders start as PENDING
            created_at=created_at,  # Current timestamp
        )

        # Order is now a complete, valid domain entity!
        # It has passed all validation rules
        # order.total is automatically calculated from items

        # STEP 6: Save order to repository
        # Persist the order so it can be retrieved later
        # In memory: stores in dictionary
        # In database: would INSERT or UPDATE in database
        self._order_repository.save_order(order)

        # STEP 7: Return the domain entity
        # Router will convert this Order to OrderResponse DTO
        # This is the reverse conversion: Entity → DTO
        return order

        # FLOW SUMMARY:
        # API request (JSON) → CreateOrderRequest (DTO) → [THIS USE CASE] →
        # Order (Entity) → [ROUTER] → OrderResponse (DTO) → API response (JSON)
        #
        # DTO → Entity → DTO
        # This is the key pattern in Clean Architecture with DTOs!

    # WHAT WE LEARNED:
    # 1. Use cases receive DTOs (CreateOrderRequest)
    # 2. Use cases return entities (Order)
    # 3. Routers handle DTO ↔ Entity conversion
    # 4. Use cases coordinate multiple repositories
    # 5. Snapshot pattern captures point-in-time data
    # 6. Domain entities validate business rules
    # 7. Validation happens at two layers (DTO format, Entity business)

    # TESTING NOTE:
    # This use case is testable without FastAPI or database:
    #
    # def test_place_order_success():
    #     # Setup fake repositories with test data
    #     fake_orders = FakeOrderRepository()
    #     fake_tables = FakeTableRepository([table1])
    #     fake_menu = FakeMenuRepository([item1, item2])
    #
    #     # Create use case
    #     use_case = PlaceOrder(fake_orders, fake_tables, fake_menu)
    #
    #     # Create request DTO
    #     request = CreateOrderRequest(
    #         table_id="table-001",
    #         items=[
    #             OrderItemInput(item_id="item-001", quantity=2)
    #         ]
    #     )
    #
    #     # Execute
    #     order = use_case.execute(request)
    #
    #     # Verify
    #     assert order.table_id == "table-001"
    #     assert len(order.items) == 1
    #     assert order.status == OrderStatus.PENDING
    #
    # def test_place_order_table_not_found():
    #     # Setup with no tables
    #     fake_orders = FakeOrderRepository()
    #     fake_tables = FakeTableRepository([])
    #     fake_menu = FakeMenuRepository([item1])
    #
    #     use_case = PlaceOrder(fake_orders, fake_tables, fake_menu)
    #
    #     request = CreateOrderRequest(table_id="table-999", items=[...])
    #
    #     # Should raise ValueError
    #     with pytest.raises(ValueError, match="Table.*not found"):
    #         use_case.execute(request)
