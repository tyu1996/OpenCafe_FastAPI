# Import Optional for type hints
from typing import Optional

# Import the repository interface (port) we're implementing
from domain.repositories.order_repository import OrderRepository

# Import the domain entity we're storing
from domain.entities.order import Order


class InMemoryOrderRepository(OrderRepository):
    """
    In-memory implementation of OrderRepository.

    This is an ADAPTER that implements the OrderRepository PORT.
    Uses a Python dictionary to store orders in RAM (not persistent).

    KEY DIFFERENCE FROM OTHER REPOSITORIES:
    - Menu and categories are READ-ONLY (we query them)
    - Tables are READ-ONLY (we query them)
    - Orders are READ-WRITE (we create new orders AND read them)

    This is the first repository where we implement WRITE operations!

    WHY IN-MEMORY FOR ORDERS?
    - Learning focus: Understand save/get operations without database
    - Fast tests: Create orders, verify save/retrieve, no cleanup
    - Development: Test order placement flow immediately
    - Simple: No transactions, locking, or concurrency to worry about

    LIMITATION: Orders are lost when server restarts!
    In Module 3, we'll replace with database persistence.

    Real-world analogy: Think of this like order tickets on a kitchen board.
    You can pin new tickets (save) and pull them down to read (get).
    But if the board falls, all tickets are lost (no persistence).

    STORAGE STRUCTURE:
    Dictionary with order ID as key, Order object as value:
    {
        "order-001": Order(id="order-001", table_id="table-001", items=[...], ...),
        "order-002": Order(id="order-002", table_id="table-003", items=[...], ...),
    }
    """

    def __init__(self):
        """
        Initialize the repository with empty storage.

        Unlike menu/category/table repositories, we DON'T pre-populate orders.

        Why no sample data?
        - Orders represent active transactions (not reference data)
        - Orders are created dynamically when customers place them
        - Starting with empty state is more realistic
        - Tests create their own orders as needed

        The empty dictionary will be populated as orders are placed.
        """
        # Store orders in a dictionary
        # Key = order ID (for fast lookup)
        # Value = Order object (complete domain entity)
        self._orders: dict[str, Order] = {}
        # Type hint dict[str, Order] documents that keys are strings, values are Orders

        # Note: In a real system, we might initialize this with:
        # - Active orders from previous session (if loading from backup)
        # - Test data for development (but we keep it clean for learning)

    def save_order(self, order: Order) -> None:
        """
        Save an order to memory.

        This implements "upsert" logic (update or insert):
        - If order.id exists: update the existing order
        - If order.id is new: create a new order

        Implementation: Simply store in dictionary (ID as key).
        Dictionary assignment handles both create and update automatically.

        Args:
            order (Order): The complete order to save.
                          Must have all fields populated (id, table_id, items, status, created_at).

        Returns:
            None: Nothing to return - order is saved.
                  If something goes wrong, raise an exception.

        Why upsert instead of separate create/update?
        - Simpler interface: one method for both operations
        - Caller doesn't need to know if order exists
        - Matches domain thinking: "save this order" (implementation detail: create or update)

        Examples:
            # Save new order
            order1 = Order(id="order-001", table_id="table-001", items=[...], ...)
            repo.save_order(order1)  # Creates new entry

            # Update existing order (e.g., change status)
            order1.status = OrderStatus.CONFIRMED  # Modify order
            repo.save_order(order1)  # Updates existing entry
        """
        # Store order in dictionary using its ID as key
        # If order.id already exists, this UPDATES it
        # If order.id is new, this CREATES it
        # This single line handles both create and update!
        self._orders[order.id] = order

        # Note: In a real database repository, this would be:
        # session.merge(order)  # SQLAlchemy upsert
        # session.commit()      # Save to database
        #
        # But here we just assign to dictionary (instant save in memory)

    def get_order_by_id(self, order_id: str) -> Optional[Order]:
        """
        Retrieve an order from memory by its ID.

        Implementation: Dictionary lookup with safe None return.

        Args:
            order_id (str): The unique ID of the order to retrieve
                           Example: "order-001" or UUID

        Returns:
            Optional[Order]: The complete Order object if found, None if not found

        Why Optional (return None instead of raising exception)?
        - "Not found" is a valid result, not an error
        - Caller can decide how to handle (404 response, error message, etc.)
        - Cleaner code: if order is None: handle_not_found()

        Examples:
            # Find existing order
            order = repo.get_order_by_id("order-001")
            if order:
                print(f"Order status: {order.status}")

            # Try to find non-existent order
            order = repo.get_order_by_id("order-999")
            # Returns None (order doesn't exist)
        """
        # dict.get(key) returns value if key exists, None if not
        # This is safer than self._orders[order_id] which raises KeyError
        return self._orders.get(order_id)

    def get_open_order_for_table(self, table_id: str) -> Optional[Order]:
        """
        Get any open order for a specific table.

        An "open" order is one that is NOT completed.
        This checks for orders in PENDING or CONFIRMED status.

        Used to enforce business rule: only one open order per table.

        Args:
            table_id: ID of the table to check

        Returns:
            Order if table has an open order, None if table is available

        Implementation: Filter dictionary values for matching table and status.
        """
        # Import OrderStatus for comparison
        from domain.entities.order import OrderStatus

        # Loop through all orders in memory
        for order in self._orders.values():
            # Check if order is for this table AND is open (not completed)
            # Open means PENDING or CONFIRMED (not COMPLETED)
            if (order.table_id == table_id and
                order.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]):
                # Found an open order for this table
                return order

        # No open order found for this table
        return None

    # Note: In Module 5, we'll expand this repository with methods like:
    #
    # def list_orders_by_table(self, table_id: str) -> List[Order]:
    #     """Get all orders for a specific table"""
    #     return [order for order in self._orders.values()
    #             if order.table_id == table_id]
    #
    # def list_orders_by_status(self, status: OrderStatus) -> List[Order]:
    #     """Get all orders with a specific status"""
    #     return [order for order in self._orders.values()
    #             if order.status == status]
    #
    # For now, we keep it simple: just save and get by ID.
