# Import FastAPI components
from fastapi import APIRouter, Depends, HTTPException  # HTTPException for error handling

# Import type hints
from typing import List

# Import our use cases from application layer
from application.use_cases.list_menu_items import ListMenuItems
from application.use_cases.get_menu_item import GetMenuItem

# Import the dependency functions that provide the use cases
from interfaces.api.dependencies import (
    get_list_menu_items_use_case,
    get_get_menu_item_use_case
)

# Import the DTO from schemas directory
# DTOs are now organized in interfaces/api/schemas/ for better structure
from interfaces.api.schemas.menu import MenuItemResponse


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

# Note: MenuItemResponse DTO has been moved to interfaces/api/schemas/menu.py
# This keeps DTOs organized in one place and avoids duplication


@router.get("/items", response_model=List[MenuItemResponse])
def list_menu_items(
    # Query parameters for filtering and searching (MODULE 4 ENHANCEMENTS)
    only_available: bool = True,  # Filter by availability (default: only available items)
    category_id: str | None = None,  # Filter by category ID (optional)
    search: str | None = None,  # Search in name and description (optional)

    # Query parameters for pagination (MODULE 4 ENHANCEMENTS)
    limit: int = 20,  # Maximum number of items to return (default: 20)
    offset: int = 0,  # Number of items to skip (default: 0, start from beginning)

    # Dependency injection - FastAPI provides configured use case
    use_case: ListMenuItems = Depends(get_list_menu_items_use_case)
):
    """
    List menu items with optional filtering, searching, and pagination.

    MODULE 4 ENHANCEMENTS:
    - Search by name or description
    - Filter by category
    - Pagination support (limit/offset)
    - Parameter validation

    Query Parameters:
        only_available (bool): If True (default), show only available items.
                              If False, show all items including out of stock.
        category_id (str, optional): Filter items by category ID (e.g., "cat-001").
        search (str, optional): Search for items with this text in name or description.
                               Case-insensitive partial matching.
        limit (int): Maximum number of items to return. Default: 20, Max: 100.
        offset (int): Number of items to skip for pagination. Default: 0.

    Returns:
        List[MenuItemResponse]: List of menu items matching filters, in JSON format

    Response Example:
        [
            {
                "id": "item-001",
                "name": "Espresso",
                "description": "Strong Italian coffee",
                "price": 2.50,
                "category": "cat-001",
                "available": true
            },
            ...
        ]

    Example Requests:
        GET /menu/items
            -> Returns first 20 available items

        GET /menu/items?search=espresso
            -> Returns available items with "espresso" in name or description

        GET /menu/items?category_id=cat-001
            -> Returns available items from category cat-001

        GET /menu/items?search=coffee&category_id=cat-001&limit=10
            -> Returns up to 10 available coffee items from category cat-001

        GET /menu/items?only_available=false&limit=50&offset=20
            -> Returns all items (available + unavailable), page 2 (items 21-70)

    Error Responses:
        400 Bad Request - Invalid parameter values (e.g., negative limit)
        422 Unprocessable Entity - Parameter type validation failed (e.g., limit="abc")
    """

    # Validate pagination parameters (MODULE 4)
    # Prevent abuse and invalid values
    if limit < 1 or limit > 100:
        # Limit must be positive and not too large
        # Too large limits waste bandwidth and slow down queries
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100"
        )

    if offset < 0:
        # Offset cannot be negative (can't skip backwards!)
        raise HTTPException(
            status_code=400,
            detail="Offset must be >= 0"
        )

    # Execute the use case with all parameters (MODULE 4 - enhanced signature)
    # The use case coordinates with repository to apply filters and pagination
    items = use_case.execute(
        only_available=only_available,  # Existing parameter from Module 3
        category_id=category_id,  # NEW in Module 4
        search=search,  # NEW in Module 4
        limit=limit,  # NEW in Module 4
        offset=offset  # NEW in Module 4
    )

    # Convert domain entities to API response models (DTOs)
    # This separates internal domain representation from external API contract
    response = [
        MenuItemResponse(
            id=item.id,
            name=item.name,
            description=item.description,
            price=item.price,
            category=item.category,
            available=item.available
        )
        for item in items
    ]

    # Return the response
    # FastAPI automatically serializes to JSON and returns HTTP 200 OK
    return response


@router.get("/items/{item_id}", response_model=MenuItemResponse)
def get_menu_item(
    # Path parameter - required part of URL
    item_id: str,  # Extracted from URL path /menu/items/{item_id}

    # Dependency injection - FastAPI provides configured use case
    use_case: GetMenuItem = Depends(get_get_menu_item_use_case)
):
    """
    Get a single menu item by ID.

    MODULE 4 NEW ENDPOINT - retrieve specific item details.

    Path Parameters:
        item_id (str): Unique identifier of the menu item

    Returns:
        MenuItemResponse: Menu item details in JSON format

    Response Example:
        {
            "id": "item-001",
            "name": "Espresso",
            "description": "Strong Italian coffee",
            "price": 2.50,
            "category": "cat-001",
            "available": true
        }

    Error Responses:
        404 Not Found - Item with given ID does not exist

    Example Requests:
        GET /menu/items/item-001
            -> Returns details for item-001

        GET /menu/items/invalid-id
            -> Returns 404 Not Found
    """

    # Execute the use case to retrieve item from repository
    item = use_case.execute(item_id=item_id)

    # Handle not found case (MODULE 4 - error handling)
    # Repository returns None when item doesn't exist
    if item is None:
        # Raise HTTP 404 Not Found error
        # FastAPI converts this to proper HTTP response
        raise HTTPException(
            status_code=404,  # Standard "not found" HTTP status
            detail=f"Menu item with ID '{item_id}' not found"  # Human-readable message
        )

    # Convert domain entity to API response DTO
    return MenuItemResponse(
        id=item.id,
        name=item.name,
        description=item.description,
        price=item.price,
        category=item.category,
        available=item.available
    )


# MODULE 4 SUMMARY:
# We added:
# 1. Search functionality (search query parameter)
# 2. Category filtering (category_id query parameter)
# 3. Pagination (limit and offset query parameters)
# 4. Parameter validation (limit 1-100, offset >= 0)
# 5. Get single item endpoint (GET /menu/items/{item_id})
# 6. Error handling (404 for not found, 400 for bad request)
#
# The router stays thin - it just handles HTTP concerns.
# Business logic lives in use cases.
# Data access lives in repositories.
# Clean architecture maintained!
