# Import FastAPI components
from fastapi import APIRouter, Depends, HTTPException, status

# Import use cases from application layer
from application.use_cases.place_order import PlaceOrder

# Import DTOs from schemas directory
from interfaces.api.schemas.orders import (
    CreateOrderRequest,
    OrderResponse,
    OrderItemResponse,
)

# Import dependency functions
from interfaces.api.dependencies import get_place_order_use_case


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


# Future endpoints we might add in Module 5:
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
