# Import Optional for type hints
from typing import Optional

# Import the domain entities we'll work with
from domain.entities.order import Order

# Import repository interface (port)
from domain.repositories.order_repository import OrderRepository


class GetOpenOrderForTable:
    """
    Use case for retrieving any open order for a specific table.

    This use case serves two purposes:
    1. **Check if table is available** before placing a new order
    2. **Show current order** for a table (customer wants to see their order)

    BUSINESS RULE ENFORCED:
    Tables can only have ONE open order at a time.
    An "open" order is one that hasn't been completed yet (PENDING or CONFIRMED).
    Once an order is COMPLETED, the table becomes available for new orders.

    This prevents:
    - Two customers accidentally ordering for the same table
    - Confusion about which order belongs to which customer
    - Billing errors (mixing up orders)

    Real-world analogy: Think of a restaurant table.
    When customers sit down and order, the table is "occupied" (has open order).
    Only when they finish and pay (order COMPLETED) does the table become available.
    You can't seat new customers at an occupied table!

    WHY A SEPARATE USE CASE?
    Could we just call get_order_by_id? No, because:
    - We don't know the order ID - we only know the table ID
    - This encodes business logic: "what counts as an open order?"
    - Different use case = different intent (checking availability vs viewing specific order)
    - Easy to enhance with business rules (e.g., timeout old orders)

    TEACHING NOTE:
    This demonstrates how use cases represent BUSINESS OPERATIONS, not just CRUD.
    "Get open order for table" is a business concept that maps to our domain model.
    """

    def __init__(self, order_repository: OrderRepository):
        """
        Initialize the use case with its dependencies.

        Args:
            order_repository: Repository for fetching orders

        DEPENDENCY INJECTION:
        Repository is injected (not created inside).
        Makes testing easy: pass fake repository in tests.
        """
        self._order_repository = order_repository

    def execute(self, table_id: str) -> Optional[Order]:
        """
        Execute the use case: retrieve any open order for a table.

        This method encapsulates the business logic:
        "Find any active order for this table."

        Args:
            table_id (str): The unique identifier of the table to check
                           Example: "table-001"

        Returns:
            Optional[Order]: The open order if table is occupied, None if available
                            - If None: table is free, can place new order
                            - If Order: table is occupied, cannot place new order

        Usage examples:

        1. Before placing order (checking availability):
        ```python
        existing_order = use_case.execute(table_id)
        if existing_order is not None:
            raise ValueError(f"Table {table_id} already has an open order")
        # OK to create new order
        ```

        2. Showing current order to customer:
        ```python
        order = use_case.execute(table_id)
        if order is None:
            return {"message": "No active order for this table"}
        return convert_to_response(order)
        ```

        BUSINESS LOGIC:
        "Open" means order status is PENDING or CONFIRMED (not COMPLETED).
        This logic is in the repository, but the use case defines WHEN to check.
        """
        # Delegate to repository
        # Repository handles the query: filter by table_id and status
        return self._order_repository.get_open_order_for_table(table_id)

    # WHAT WE LEARNED:
    # 1. Use cases represent business operations, not just CRUD
    # 2. "Get open order for table" is a business concept
    # 3. Encapsulates business rule: "what counts as open?"
    # 4. Returning Optional makes "no order" explicit
    # 5. Same pattern as GetOrder but different business intent

    # WHY NOT JUST USE GET_ORDER_BY_ID?
    # - Different question: "Is table available?" vs "Show me order X"
    # - We know table ID, not order ID
    # - Business logic: filtering by status (open vs closed)
    # - Future enhancements: timeout old orders, priority tables, etc.
