# Import FastAPI components
from fastapi import APIRouter, Depends, HTTPException, status

# Import use cases from application layer
from application.use_cases.place_order import PlaceOrder
from application.use_cases.get_order import GetOrder  # MODULE 5
from application.use_cases.get_open_order_for_table import GetOpenOrderForTable  # MODULE 5

# Import DTOs from schemas directory
from interfaces.api.schemas.orders import (
    CreateOrderRequest,
    OrderResponse,
    OrderItemResponse,
    OrderPricingResponse,  # MODULE 5
    LineItemPriceResponse,  # MODULE 5
)

# Import dependency functions
from interfaces.api.dependencies import (
    get_place_order_use_case,
    get_get_order_use_case,  # MODULE 5
    get_get_open_order_for_table_use_case,  # MODULE 5
    get_pricing_service,  # MODULE 5
)


"""
Orders Router - API endpoints for order operations

This is the INTERFACE LAYER:
- Handles HTTP concerns (routes, status codes, error responses)
- Converts between domain entities and DTOs
- Thin layer: delegates business logic to use cases

KEY TEACHING POINTS:
1. DTO → Entity → DTO conversion flow
2. Error handling and HTTP status codes
3. Request validation (Pydantic) vs business validation (domain)
"""

# Create the router for order-related endpoints
router = APIRouter(
    prefix="/orders",  # All routes start with /orders
    tags=["orders"]    # Groups endpoints in OpenAPI docs under "orders"
)


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    request: CreateOrderRequest,  # Pydantic automatically validates request body
    use_case: PlaceOrder = Depends(get_place_order_use_case),  # Dependency injection
):
    """
    Create a new order.

    This endpoint demonstrates the complete DTO → Entity → DTO flow!

    Request body (DTO):
    {
        "table_id": "table-001",
        "items": [
            {"item_id": "item-001", "quantity": 2},
            {"item_id": "item-003", "quantity": 1}
        ]
    }

    Response (DTO):
    {
        "id": "order-123",
        "table_id": "table-001",
        "items": [
            {
                "menu_item_id": "item-001",
                "menu_item_name": "Espresso",
                "unit_price": 2.50,
                "quantity": 2,
                "subtotal": 5.00
            },
            ...
        ],
        "status": "pending",
        "created_at": "2024-01-15T14:30:00",
        "total": 8.50
    }

    HOW THIS WORKS (The complete flow):

    1. Client sends JSON request body
    2. Pydantic validates format (CreateOrderRequest DTO)
       - Is table_id a string?
       - Is items a list with at least 1 item?
       - Are quantities positive integers?
       - This is LAYER 1 VALIDATION (format/type)

    3. FastAPI injects PlaceOrder use case via dependency injection

    4. We call use_case.execute(request) passing the DTO

    5. Use case performs LAYER 2 VALIDATION (business rules):
       - Does table exist?
       - Do menu items exist?
       - Are items available?

    6. Use case creates Order domain entity with OrderItems
       - Snapshots prices from menu
       - Generates order ID
       - Sets initial status to PENDING

    7. Use case saves order and returns Order entity

    8. We convert Order entity → OrderResponse DTO
       - Map Order fields to response fields
       - Convert OrderItem entities to OrderItemResponse DTOs
       - Convert OrderStatus enum to string

    9. FastAPI serializes OrderResponse to JSON

    10. FastAPI returns HTTP 201 Created with JSON body

    This is the KEY PATTERN: DTO → Entity → DTO
    """

    try:
        # Execute use case with the DTO
        # Use case returns Order domain entity (not DTO!)
        order = use_case.execute(request)

        # Convert Order entity → OrderResponse DTO
        # This is the reverse conversion from what happened in the use case
        # Use case did: DTO → Entity
        # Now we do: Entity → DTO

        # Convert each OrderItem entity to OrderItemResponse DTO
        item_responses = [
            OrderItemResponse(
                menu_item_id=item.menu_item_id,  # From entity
                menu_item_name=item.menu_item_name,  # Snapshot from entity
                unit_price=item.unit_price,  # Snapshot from entity
                quantity=item.quantity,  # From entity
                subtotal=item.subtotal,  # Calculated property from entity
            )
            for item in order.items  # Loop through OrderItem entities
        ]

        # Create OrderResponse DTO from Order entity
        response = OrderResponse(
            id=order.id,  # Generated UUID from entity
            table_id=order.table_id,  # From entity
            items=item_responses,  # Converted DTOs (not entities!)
            status=order.status.value,  # Convert enum to string: OrderStatus.PENDING → "pending"
            created_at=order.created_at,  # Timestamp from entity
            total=order.total,  # Calculated property from entity
        )

        # Return DTO (FastAPI serializes to JSON)
        # HTTP 201 Created is set via status_code parameter above
        return response

    except ValueError as e:
        # Use case raises ValueError for business validation failures:
        # - Table not found
        # - Menu item not found
        # These are client errors (bad request), so return 400
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)  # Error message from use case
        )

    # Note: Other exceptions would propagate up and FastAPI would return 500
    # In production, you'd add logging and more specific error handling

    # WHAT WE LEARNED:
    # 1. Request comes in as DTO (CreateOrderRequest)
    # 2. Use case receives DTO, returns entity (Order)
    # 3. Router converts entity back to DTO (OrderResponse)
    # 4. DTO → Entity → DTO is the complete flow
    # 5. Two layers of validation: Pydantic (format) + Domain (business)
    # 6. Error handling maps domain errors to HTTP status codes


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: str,  # Path parameter (required)
    use_case: GetOrder = Depends(get_get_order_use_case),  # Dependency injection
):
    """
    Get details of a specific order by ID.

    MODULE 5 NEW ENDPOINT - Retrieve order details.

    This demonstrates simple entity retrieval with clean architecture.

    Args:
        order_id: Unique identifier of the order
        use_case: GetOrder use case (injected by FastAPI)

    Returns:
        OrderResponse: Complete order details with items and pricing

    Raises:
        404: Order not found

    Example request:
        GET /orders/order-123

    Example response:
        {
            "id": "order-123",
            "table_id": "table-001",
            "items": [
                {
                    "menu_item_id": "item-001",
                    "menu_item_name": "Espresso",
                    "unit_price": 2.50,
                    "quantity": 2,
                    "subtotal": 5.00
                }
            ],
            "status": "pending",
            "created_at": "2024-01-15T14:30:00",
            "total": 5.00
        }

    FLOW:
    1. Client requests order by ID
    2. Router calls use case with order_id
    3. Use case calls repository.get_order_by_id()
    4. Repository queries database
    5. Repository returns Order entity or None
    6. Use case returns Order entity or None
    7. Router converts Order to OrderResponse DTO
    8. FastAPI serializes DTO to JSON

    ERROR HANDLING:
    - 404 if order doesn't exist
    - 422 if order_id format is invalid (FastAPI validation)
    """
    # Execute use case to get order entity
    order = use_case.execute(order_id=order_id)

    # Check if order was found
    if order is None:
        # Raise 404 Not Found with clear message
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID '{order_id}' not found"
        )

    # Convert Order entity → OrderResponse DTO
    # This is the same conversion as in create_order endpoint
    item_responses = [
        OrderItemResponse(
            menu_item_id=item.menu_item_id,
            menu_item_name=item.menu_item_name,
            unit_price=item.unit_price,
            quantity=item.quantity,
            subtotal=item.subtotal,
        )
        for item in order.items
    ]

    response = OrderResponse(
        id=order.id,
        table_id=order.table_id,
        items=item_responses,
        status=order.status.value,  # Convert enum to string
        created_at=order.created_at,
        total=order.total,
    )

    return response


@router.get("/{order_id}/pricing", response_model=OrderPricingResponse)
def get_order_pricing(
    order_id: str,  # Path parameter (required)
    use_case: GetOrder = Depends(get_get_order_use_case),  # Get order
    pricing_service = Depends(get_pricing_service),  # Pricing service
):
    """
    Get detailed pricing breakdown for an order.

    MODULE 5 NEW ENDPOINT - Demonstrates pricing engine with discount logic.

    This endpoint shows how prices are calculated step-by-step.
    Provides transparency for customers to understand their bill.

    Args:
        order_id: Unique identifier of the order
        use_case: GetOrder use case (injected)
        pricing_service: PricingService (injected)

    Returns:
        OrderPricingResponse: Itemized pricing with discounts

    Raises:
        404: Order not found

    Example response:
        {
            "line_items": [
                {
                    "item_name": "Espresso",
                    "quantity": 2,
                    "unit_price": 2.50,
                    "subtotal": 5.00
                }
            ],
            "subtotal": 5.00,
            "discount_amount": 0.50,
            "discount_reason": "10% discount applied",
            "total": 4.50
        }

    FLOW - PRICING ENGINE PATTERN:
    1. Get order from repository
    2. Pass order to pricing service
    3. Pricing service calculates:
       - Line item subtotals
       - Order subtotal
       - Discount amount
       - Final total
    4. Return itemized breakdown

    WHY SEPARATE ENDPOINT?
    - Some clients want simple total (GET /orders/{id})
    - Some clients want detailed breakdown (this endpoint)
    - Keeps responses focused and efficient
    - Easy to add more pricing endpoints (e.g., preview pricing before ordering)
    """
    # Get order entity
    order = use_case.execute(order_id=order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID '{order_id}' not found"
        )

    # Calculate pricing with discount logic
    # PricingService handles all pricing business rules
    pricing = pricing_service.calculate_order_pricing(order)

    # Convert domain service output → DTO
    line_item_responses = [
        LineItemPriceResponse(
            item_name=item.item_name,
            quantity=item.quantity,
            unit_price=item.unit_price,
            subtotal=item.subtotal,
        )
        for item in pricing.line_items
    ]

    response = OrderPricingResponse(
        line_items=line_item_responses,
        subtotal=pricing.subtotal,
        discount_amount=pricing.discount_amount,
        discount_reason=pricing.discount_reason,
        total=pricing.total,
    )

    return response


# MODULE 5 NOTE:
# We could add GET /tables/{table_id}/open-order to the tables router,
# but for now we keep it here since it's order-focused.
# Future refactoring might move it to make REST structure cleaner.


# Future endpoints for Module 6 (Auth) and Module 7 (Advanced):
#
# @router.get("/{order_id}", response_model=OrderResponse)
# def get_order(
#     order_id: str,
#     use_case: GetOrder = Depends(get_get_order_use_case)
# ):
#     """Get details of a specific order by ID."""
#     order = use_case.execute(order_id)
#     if order is None:
#         raise HTTPException(status_code=404, detail="Order not found")
#     return convert_order_to_response(order)
#
# @router.get("", response_model=List[OrderResponse])
# def list_orders(
#     table_id: str | None = None,
#     status: str | None = None,
# ):
#     """List orders, optionally filtered by table or status."""
#     # ...
#
# @router.patch("/{order_id}/status")
# def update_order_status(
#     order_id: str,
#     new_status: str,
# ):
#     """Update order status (PENDING → CONFIRMED → PREPARING → READY → COMPLETED)."""
#     # ...
