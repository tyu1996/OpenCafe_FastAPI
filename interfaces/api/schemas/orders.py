# Import datetime for timestamp fields
from datetime import datetime

# Import Decimal for precise money handling
from decimal import Decimal

# Import List and Optional for type hints
from typing import List, Optional

# Import Pydantic BaseModel and validation helpers
from pydantic import BaseModel, Field, field_serializer


class OrderItemInput(BaseModel):
    """
    DTO for order item INPUT (what clients send when placing orders).

    This represents ONE item in an order as provided by the client.
    Client sends: "I want item X with quantity Y"

    WHY THIS EXISTS:
    - Clients don't know (or care) about item names or prices
    - Clients just specify ID and quantity
    - Server looks up name and price from menu
    - This is the API CONTRACT for what clients must send

    Real-world analogy: Customer points at menu and says "2 of item #5".
    They don't need to say "2 Espressos at $2.50 each" - we look that up.

    VALIDATION:
    - Pydantic validates item_id is a string
    - Pydantic validates quantity is an int >= 1
    - Business validation (item exists in menu) happens in use case

    TWO-LAYER VALIDATION STRATEGY:
    Layer 1 (Pydantic/DTO): Format validation (is it an int? is it positive?)
    Layer 2 (Domain/Entity): Business validation (does item exist? is it available?)
    """

    # ID of the menu item to order
    # Example: "item-001" or "espresso"
    # Client must know this ID (from GET /menu/items)
    item_id: str

    # How many of this item to order
    # Must be at least 1 (can't order 0 or negative items)
    # Field(ge=1) means "greater than or equal to 1"
    quantity: int = Field(ge=1)

    # Note: We DON'T include name or price here
    # Those are looked up from the menu by the server
    # This keeps the API simple for clients

    # Example JSON input:
    # {
    #   "item_id": "item-001",
    #   "quantity": 2
    # }


class CreateOrderRequest(BaseModel):
    """
    DTO for CREATE ORDER request (what clients send to POST /orders).

    This represents the ENTIRE order data from the client.
    Client sends: "Create order for table X with these items"

    WHY THIS EXISTS:
    - Defines the API contract for placing orders
    - Separates API format from domain model
    - Pydantic validates request format before domain logic runs

    VALIDATION:
    - table_id must be a string
    - items must be a list with at least 1 item
    - Each item must be a valid OrderItemInput

    Real-world analogy: This is like the order form customers fill out:
    - Table number: ___
    - Items: [list of items with quantities]

    TWO-LAYER VALIDATION:
    Layer 1 (Pydantic/here): Format validation
      - Is table_id a string?
      - Is items a list?
      - Are there at least 1 items?
      - Is each quantity positive?

    Layer 2 (Domain/use case): Business validation
      - Does the table exist?
      - Are the menu items valid and available?
      - Can we create this order right now?
    """

    # ID of the table this order is for
    # Example: "table-001"
    # Client must specify which table (from GET /tables)
    table_id: str

    # List of items to order
    # Must have at least 1 item (can't place empty order)
    # Field(min_length=1) enforces at least one item
    items: List[OrderItemInput] = Field(min_length=1)

    # Note: We DON'T include:
    # - order_id (server generates this)
    # - status (server sets to PENDING initially)
    # - created_at (server sets to current time)
    # - total (server calculates from items)
    # Client only provides: table and items

    # Example JSON input:
    # {
    #   "table_id": "table-001",
    #   "items": [
    #     {"item_id": "item-001", "quantity": 2},
    #     {"item_id": "item-003", "quantity": 1}
    #   ]
    # }


class OrderItemResponse(BaseModel):
    """
    DTO for order item OUTPUT (what server returns in order responses).

    This represents ONE item in an order as returned to clients.
    Server returns: "Item X: name, price, quantity, subtotal"

    WHY DIFFERENT FROM OrderItemInput?
    - Input: minimal data (just ID and quantity)
    - Output: complete data (ID, name, price, quantity, subtotal)
    - Clients need full details to display orders

    This mirrors the OrderItem domain entity but in DTO form.

    Real-world analogy: Input is "2 of item #5", output is
    "2x Espresso @ $2.50 each = $5.00 subtotal"
    """

    # ID of the menu item (reference to MenuItem)
    # Example: "item-001"
    menu_item_id: str

    # Name of the item (snapshot at order time)
    # Example: "Espresso"
    # This is the name that was current when order was placed
    menu_item_name: str

    # Price per unit (snapshot at order time)
    # Example: Decimal("2.50")
    # This is the price that was current when order was placed
    unit_price: Decimal = Field(decimal_places=2)

    # Quantity ordered
    # Example: 2
    quantity: int

    # Subtotal for this item (unit_price × quantity)
    # Example: Decimal("5.00") for 2 × $2.50
    # Calculated and included for client convenience
    subtotal: Decimal = Field(decimal_places=2)

    @field_serializer("unit_price", "subtotal")
    def serialize_decimal(self, value: Decimal, _info) -> float:
        """
        Convert Decimal fields to float for JSON serialization.

        JSON doesn't support Decimal, only float/number.
        This serializer handles unit_price and subtotal fields.
        """
        return float(value)

    # Example JSON output:
    # {
    #   "menu_item_id": "item-001",
    #   "menu_item_name": "Espresso",
    #   "unit_price": 2.50,
    #   "quantity": 2,
    #   "subtotal": 5.00
    # }


class OrderResponse(BaseModel):
    """
    DTO for complete order OUTPUT (what server returns from GET /orders/{id}).

    This represents the ENTIRE order as returned to clients.
    Server returns: "Order X for table Y, status Z, items [...], total $$$"

    WHY THIS EXISTS:
    - Defines the API contract for order responses
    - Separates API format from domain Order entity
    - Allows API evolution without changing domain

    This mirrors the Order domain entity but in DTO form.

    Real-world analogy: This is like the printed receipt customers get:
    - Order number
    - Table number
    - Date/time
    - List of items with prices
    - Total
    - Status (pending/ready/etc.)

    CONVERSION FROM DOMAIN:
    In the router, we convert Order entity → OrderResponse DTO:
    ```python
    order = use_case.execute(...)  # Returns Order entity
    response = OrderResponse(       # Convert to DTO
        id=order.id,
        table_id=order.table_id,
        items=[...],  # Convert each OrderItem to OrderItemResponse
        status=order.status.value,
        created_at=order.created_at,
        total=order.total
    )
    ```
    """

    # Unique identifier for this order
    # Example: "order-001" or UUID
    # Generated by server when order is created
    id: str

    # ID of the table this order belongs to
    # Example: "table-001"
    table_id: str

    # List of items in this order
    # Each item shows full details (name, price, quantity, subtotal)
    items: List[OrderItemResponse]

    # Current status of the order
    # Example: "pending", "confirmed", "preparing", "ready", "completed"
    # Returned as string (enum value) for simplicity
    status: str

    # When this order was created
    # Example: "2024-01-15T14:30:00"
    # Pydantic automatically handles datetime serialization to ISO format
    created_at: datetime

    # Total price for entire order (sum of all item subtotals)
    # Example: Decimal("8.50")
    # Included for client convenience (could be calculated from items)
    total: Decimal = Field(decimal_places=2)

    @field_serializer("total")
    def serialize_total(self, value: Decimal, _info) -> float:
        """
        Convert Decimal total to float for JSON serialization.
        """
        return float(value)

    # Example JSON output:
    # {
    #   "id": "order-001",
    #   "table_id": "table-001",
    #   "items": [
    #     {
    #       "menu_item_id": "item-001",
    #       "menu_item_name": "Espresso",
    #       "unit_price": 2.50,
    #       "quantity": 2,
    #       "subtotal": 5.00
    #     },
    #     {
    #       "menu_item_id": "item-003",
    #       "menu_item_name": "Croissant",
    #       "unit_price": 3.50,
    #       "quantity": 1,
    #       "subtotal": 3.50
    #     }
    #   ],
    #   "status": "pending",
    #   "created_at": "2024-01-15T14:30:00",
    #   "total": 8.50
    # }


class LineItemPriceResponse(BaseModel):
    """
    DTO for line item pricing breakdown in OrderPricingResponse.

    Shows how each item's price was calculated.
    This provides transparency for customers.

    MODULE 5 - Pricing Engine
    """
    # Name of the item
    item_name: str

    # Quantity ordered
    quantity: int

    # Price per item
    unit_price: Decimal = Field(decimal_places=2)

    # Total for this line item (unit_price × quantity)
    subtotal: Decimal = Field(decimal_places=2)

    @field_serializer("unit_price", "subtotal")
    def serialize_decimal(self, value: Decimal, _info) -> float:
        """Convert Decimal to float for JSON."""
        return float(value)


class OrderPricingResponse(BaseModel):
    """
    DTO for order pricing breakdown.

    Shows itemized pricing with discounts applied.
    Used for transparent pricing display to customers.

    MODULE 5 - Pricing Engine
    """
    # Breakdown of each line item
    line_items: List[LineItemPriceResponse]

    # Total before discount
    subtotal: Decimal = Field(decimal_places=2)

    # Discount amount (0 if no discount)
    discount_amount: Decimal = Field(decimal_places=2)

    # Why discount was applied (None if no discount)
    discount_reason: Optional[str] = None

    # Final total after discount
    total: Decimal = Field(decimal_places=2)

    @field_serializer("subtotal", "discount_amount", "total")
    def serialize_decimal(self, value: Decimal, _info) -> float:
        """Convert Decimal to float for JSON."""
        return float(value)
