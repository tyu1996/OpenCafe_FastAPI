# Import Optional for type hints
# Optional[Order] means "either an Order or None"
from typing import Optional

# Import the domain entities we'll work with
from domain.entities.order import Order

# Import repository interface (port)
from domain.repositories.order_repository import OrderRepository


class GetOrder:
    """
    Use case for retrieving an order by its ID.

    This is a SIMPLE USE CASE - it's just a thin wrapper around the repository.
    You might wonder: "Why not call the repository directly from the router?"

    REASONS FOR THIS USE CASE LAYER (even when simple):
    1. **Consistency**: All business operations go through use cases (uniform pattern)
    2. **Future extensibility**: Easy to add business logic later without changing router
       - Log access for auditing
       - Check user permissions
       - Track analytics
       - Add caching
    3. **Testing**: Can test business behavior separate from HTTP concerns
    4. **Dependency inversion**: Router depends on abstraction (use case), not concrete repository

    Real-world analogy: Think of a restaurant manager checking order details.
    The manager doesn't dig through filing cabinets (repository).
    They ask a staff member (use case) who handles the details.
    If policies change (e.g., "only show orders to authorized staff"),
    the staff member (use case) can enforce that without changing
    how the manager asks for orders (router).

    TEACHING NOTE:
    Module 5 focuses on simple retrieval before adding complexity.
    In Module 6 (Auth), we might enhance this to:
    - Check if user is authorized to view this order
    - Log access for audit trail
    - Return sanitized data based on user role
    """

    def __init__(self, order_repository: OrderRepository):
        """
        Initialize the use case with its dependencies.

        Args:
            order_repository: Repository for fetching orders

        DEPENDENCY INJECTION:
        Repository is injected (not created inside).
        This makes testing easy: pass fake repository in tests.
        """
        # Store repository for later use
        self._order_repository = order_repository

    def execute(self, order_id: str) -> Optional[Order]:
        """
        Execute the use case: retrieve an order by ID.

        This is straightforward: delegate to repository.
        No complex business logic needed for simple retrieval.

        Args:
            order_id (str): The unique identifier of the order to retrieve
                           Example: "order-001" or UUID

        Returns:
            Optional[Order]: The order if found, None if not found
                            Caller (router) decides how to handle None (typically 404)

        Why return Optional instead of raising exception?
        - "Not found" is not an error in the business sense
        - It's a normal scenario: user might have typo, wrong ID, etc.
        - Router can decide appropriate HTTP status (404)
        - Cleaner separation: use case returns data, router handles HTTP concerns

        Example flow:
        1. Router calls: order = use_case.execute("order-123")
        2. Use case calls: order = repository.get_order_by_id("order-123")
        3. Repository queries database and returns Order or None
        4. Use case returns Order or None
        5. Router converts Order to DTO or raises HTTPException(404)
        """
        # Simply delegate to repository
        # Repository handles the query logic (SQL, filtering, etc.)
        return self._order_repository.get_order_by_id(order_id)

    # WHAT WE LEARNED:
    # 1. Not all use cases are complex - some are simple delegation
    # 2. Use cases provide consistency and extensibility points
    # 3. Returning Optional instead of exceptions for "not found" cases
    # 4. Clean separation: use case handles business, router handles HTTP

    # WHY NOT SKIP THIS LAYER?
    # Even though this use case is simple now, having it allows us to:
    # - Add authorization checks without touching the router
    # - Add caching without changing the repository
    # - Add audit logging in one place
    # - Keep the router thin and focused on HTTP concerns
    #
    # Example future enhancement (Module 6):
    # def execute(self, order_id: str, user_id: str) -> Optional[Order]:
    #     order = self._order_repository.get_order_by_id(order_id)
    #     if order and not self._is_authorized(user_id, order):
    #         raise UnauthorizedError("Cannot view this order")
    #     return order
