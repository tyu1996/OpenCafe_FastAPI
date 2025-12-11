# Import ABC (Abstract Base Class) and abstractmethod for defining interfaces
from abc import ABC, abstractmethod

# Import Optional for type hints
# Optional[Order] means "either an Order or None"
from typing import Optional

# Import the domain entity this repository manages
from domain.entities.order import Order


class OrderRepository(ABC):
    """
    OrderRepository defines the interface (contract) for persisting and retrieving orders.

    This is a PORT in the ports & adapters pattern.
    It defines WHAT operations we need for order persistence,
    but not HOW they're stored (memory, database, file, etc.).

    WHY SAVE AND GET?
    Unlike MenuRepository (read-only), orders need to be created and persisted.
    Customers place new orders (write operation) and staff retrieve them (read operation).

    Real-world analogy: Think of this like the order ticket system in a restaurant.
    You can "save a new ticket" (pin it to the kitchen board) and "retrieve a ticket"
    (pull it down to check details), but the system doesn't specify whether it's
    physical tickets, a tablet system, or a printed order queue.

    NOTE: This is a simplified repository for Module 2.
    A production system might also have:
    - list_orders_by_table(table_id: str)
    - list_orders_by_status(status: OrderStatus)
    - update_order_status(order_id: str, new_status: OrderStatus)
    - delete_order(order_id: str)
    We keep it minimal for learning purposes.
    """

    @abstractmethod
    def save_order(self, order: Order) -> None:
        """
        Save a new order to the persistent store.

        This method persists an order so it can be retrieved later.
        In a real system, this writes to a database.
        In tests, this might store in a dictionary.

        Args:
            order (Order): The order entity to save.
                          Must be a complete, valid Order with all fields.

        Returns:
            None: This method doesn't return anything.
                  The order is saved, and the caller can assume success.
                  If saving fails, the implementation should raise an exception.

        Why no return value?
        - The order ID is already part of the Order object
        - Caller already has the order, doesn't need it returned
        - Simpler interface: save and forget
        - Exceptions handle errors (no need to check return value)

        IMPORTANT: This method should handle BOTH create and update.
        If an order with this ID already exists, update it.
        If it doesn't exist, create it.
        This is called "upsert" (update or insert).

        Why upsert instead of separate create/update methods?
        - Simpler interface: one method to remember
        - Caller doesn't need to know if order exists already
        - Matches domain thinking: "save this order" (don't care about storage details)

        Implementation notes for adapters:
        - Validate that order.id is not empty/None
        - Store all Order fields (id, table_id, items, status, created_at)
        - Handle duplicate IDs (update existing, don't error)
        - Make sure items list is preserved correctly
        """
        pass  # Abstract method - no implementation here

    @abstractmethod
    def get_order_by_id(self, order_id: str) -> Optional[Order]:
        """
        Retrieve an order by its unique ID.

        This method looks up a previously saved order.
        Used to show order details, check status, or update order.

        Args:
            order_id (str): The unique identifier of the order to retrieve
                           Example: "order-001" or a UUID like "123e4567-e89b-12d3-a456-426614174000"

        Returns:
            Optional[Order]: The order if found, None if not found

        Why Optional?
        - Not all order IDs exist (invalid, typos, deleted orders)
        - None clearly signals "order not found" without raising exception
        - Caller can decide how to handle: return 404, show error, etc.

        Example usage in a use case:
        ```python
        order = repository.get_order_by_id("order-123")
        if order is None:
            raise ValueError("Order not found")
        return order
        ```

        Implementation notes for adapters:
        - Return None if order doesn't exist (don't raise exception)
        - Return a complete Order object with ALL fields populated:
          - id, table_id, items (full list), status, created_at
        - Items should be OrderItem objects, not dictionaries
        - Status should be OrderStatus enum, not string
        """
        pass  # Abstract method - no implementation here

    @abstractmethod
    def get_open_order_for_table(self, table_id: str) -> Optional[Order]:
        """
        Get any open (non-completed) order for a specific table.

        This method checks if a table already has an active order.
        Used to prevent multiple open orders for the same table (business rule).

        "Open" means order is in PENDING or CONFIRMED status (not COMPLETED).
        Once an order is COMPLETED, the table is available for new orders.

        Args:
            table_id (str): The ID of the table to check

        Returns:
            Optional[Order]: The open order if one exists, None if table is available

        Why this method?
        - Business rule: tables can only have one active order at a time
        - Prevents race condition where two customers try to order for same table
        - Use before creating new order: "Is this table already occupied?"

        Example usage in PlaceOrder use case:
        ```python
        existing_order = repository.get_open_order_for_table(table_id)
        if existing_order is not None:
            raise ValueError(f"Table {table_id} already has an open order")
        # Proceed to create new order
        ```

        Implementation notes:
        - Query for orders where table_id matches AND status is PENDING or CONFIRMED
        - Return first match (should only be one per business rule)
        - Return None if no open orders found
        """
        pass

    # Note: Future enhancements might include:
    # - list_orders_by_table(table_id: str) -> List[Order]
    # - list_orders_by_status(status: OrderStatus) -> List[Order]
    # - update_order_status(order_id: str, status: OrderStatus) -> None
