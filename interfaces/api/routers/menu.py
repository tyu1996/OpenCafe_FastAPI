# Import FastAPI components
from fastapi import APIRouter, Depends  # Depends is used for dependency injection

# Import type hints
from typing import List

# Import Pydantic for request/response models
# Pydantic models handle validation and serialization at the API boundary
from pydantic import BaseModel, Field, field_serializer

# Import Decimal for monetary values
from decimal import Decimal

# Import our use case from application layer
from application.use_cases.list_menu_items import ListMenuItems

# Import the dependency function that provides the use case
from interfaces.api.dependencies import get_list_menu_items_use_case


"""
Menu Router - API endpoints for menu operations

This is the INTERFACE LAYER (outermost layer in Clean Architecture):
- Handles HTTP concerns (routes, status codes, serialization)
- Converts between domain entities and API request/response formats
- Does NOT contain business logic (that's in use cases)
- Thin layer: just coordinates between HTTP and application layer

SEPARATION OF CONCERNS:
- Domain entities (MenuItem): pure business objects
- Pydantic models (MenuItemResponse): API data transfer objects (DTOs)
- Why separate? Domain might evolve differently from API
  Example: domain adds fields we don't want to expose in API
"""


# Create the router for menu-related endpoints
router = APIRouter(
    prefix="/menu",  # All routes start with /menu
    tags=["menu"]    # Groups endpoints in OpenAPI docs under "menu"
)


class MenuItemResponse(BaseModel):
    """
    Pydantic response model for a menu item.

    This is a DATA TRANSFER OBJECT (DTO):
    - Used at the API boundary (HTTP requests/responses)
    - Separate from domain entity (MenuItem)
    - Handles JSON serialization/validation

    WHY SEPARATE FROM DOMAIN ENTITY?
    - Domain entity (MenuItem): represents business concept
    - Response model (this): represents API contract
    - They might evolve independently
    - API might hide/transform some fields
    - API might combine multiple entities
    - Domain stays pure, API layer handles HTTP concerns

    Example differences:
    - Domain might have internal IDs we don't expose
    - API might format dates differently
    - API might add computed fields (like full_url)
    - Domain might have methods, DTOs are just data
    """

    # Unique identifier for the menu item
    id: str

    # Display name shown to customers
    name: str

    # Brief description of the item
    description: str

    # Price with exactly 2 decimal places (e.g., 2.50 not 2.5)
    # Field() lets us add validation and metadata
    # decimal_places=2 ensures consistent formatting: $2.50, not $2.5 or $2.500
    price: Decimal = Field(decimal_places=2)

    # Category this item belongs to (e.g., "coffee", "pastry")
    category: str

    # Whether item is currently available to order
    available: bool

    # Custom serializer for Decimal fields
    # Pydantic v2 requires explicit serialization for Decimal types
    # This converts Decimal to float for JSON (float is standard for API responses)
    @field_serializer('price')
    def serialize_price(self, price: Decimal, _info):
        """Convert Decimal price to float for JSON serialization."""
        return float(price)
        # Note: In production APIs dealing with money, you might prefer:
        # return str(price)  # Keeps exact precision, avoids float rounding issues
        # But float is more convenient for most API clients

    # Future: we might add computed fields
    # @property
    # def formatted_price(self) -> str:
    #     """Return price formatted as currency"""
    #     return f"${self.price:.2f}"


@router.get("/items", response_model=List[MenuItemResponse])
def list_menu_items(
    only_available: bool = True,  # Query parameter with default value
    use_case: ListMenuItems = Depends(get_list_menu_items_use_case)  # DI magic happens here!
):
    """
    List all menu items, optionally filtered by availability.

    Query Parameters:
        only_available (bool): If True (default), show only available items.
                              If False, show all items including out of stock.

    Returns:
        List[MenuItemResponse]: List of menu items in JSON format

    Response Example:
        [
            {
                "id": "item-001",
                "name": "Espresso",
                "description": "Strong Italian coffee",
                "price": 2.50,
                "category": "coffee",
                "available": true
            },
            ...
        ]

    HOW THIS WORKS:

    1. FastAPI receives HTTP GET request to /menu/items?only_available=true
    2. FastAPI parses query parameter only_available as boolean
    3. FastAPI calls get_list_menu_items_use_case() to get the use case
    4. FastAPI injects the use case into the 'use_case' parameter
    5. Our function executes the use case
    6. Use case returns List[MenuItem] (domain entities)
    7. We convert domain entities to MenuItemResponse (DTOs)
    8. FastAPI serializes to JSON
    9. FastAPI returns HTTP 200 with JSON body

    WHAT HAPPENS IN THIS FUNCTION:
    - We coordinate between HTTP and application layer
    - We convert domain entities to API response format
    - We do NOT implement business logic here (that's in use case)
    """

    # Step 1: Execute the use case (application layer handles business logic)
    # The use case returns domain entities (MenuItem objects)
    # The only_available parameter is passed to the use case for filtering
    items = use_case.execute(only_available=only_available)

    # Step 2: Convert domain entities to API response models (DTOs)
    # Why convert?
    # - Domain entities might have internal fields we don't want to expose
    # - API models have Pydantic validation and serialization
    # - Separates API contract from domain model
    # - If domain changes, API can stay stable (backwards compatibility)

    # List comprehension: create MenuItemResponse for each MenuItem
    response = [
        MenuItemResponse(
            id=item.id,          # Copy id from domain entity
            name=item.name,      # Copy name
            description=item.description,  # Copy description
            price=item.price,    # Copy price (stays as Decimal)
            category=item.category,  # Copy category
            available=item.available  # Copy availability flag
        )
        for item in items  # For each domain entity in the list
    ]

    # Step 3: Return the list of response models
    # FastAPI automatically:
    # - Validates the response matches response_model (List[MenuItemResponse])
    # - Serializes to JSON
    # - Sets Content-Type header to application/json
    # - Returns HTTP 200 OK
    return response

    # Note: We could make this more concise:
    # return [MenuItemResponse(**item.__dict__) for item in items]
    # But explicit is better than implicit for clarity
    # (Especially in teaching code!)


# Future endpoints we might add:
#
# @router.get("/items/{item_id}", response_model=MenuItemResponse)
# def get_menu_item(
#     item_id: str,
#     use_case: GetMenuItem = Depends(get_get_menu_item_use_case)
# ):
#     """Get details of a single menu item by ID."""
#     item = use_case.execute(item_id=item_id)
#     if item is None:
#         raise HTTPException(status_code=404, detail="Item not found")
#     return MenuItemResponse(**item.__dict__)
#
# @router.get("/categories")
# def list_categories():
#     """List all menu categories."""
#     # ...
#
# @router.get("/items/search")
# def search_menu_items(q: str):
#     """Search menu items by name or description."""
#     # ...
