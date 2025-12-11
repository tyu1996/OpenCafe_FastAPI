# Import Decimal for precise money handling
from decimal import Decimal

# Import Pydantic BaseModel for API request/response validation
# Pydantic is FastAPI's validation library
from pydantic import BaseModel, Field, field_serializer


class MenuCategoryResponse(BaseModel):
    """
    DTO (Data Transfer Object) for menu category API responses.

    This is a PYDANTIC MODEL that defines the API contract for categories.
    MODULE 4: Used for GET /menu/categories and GET /menu/categories/{id}/items

    WHY SEPARATE FROM MenuCategory ENTITY?
    - Layer separation: API contracts live in interfaces/, not domain/
    - Framework independence: domain doesn't depend on Pydantic
    - API flexibility: can reshape data for API without changing domain

    WHEN TO USE THIS:
    - Returning data from GET /menu/categories
    - Returning data from GET /menu/categories/{id}
    """

    # Unique identifier for this category
    # Example: "cat-001" or "coffee-drinks"
    id: str

    # Display name of the category
    # Example: "Coffee Drinks", "Pastries"
    name: str

    # Brief description of the category
    # Example: "Hot and cold coffee beverages"
    description: str

    # Example JSON output:
    # {
    #   "id": "cat-001",
    #   "name": "Coffee Drinks",
    #   "description": "Hot and cold coffee beverages"
    # }


class MenuItemResponse(BaseModel):
    """
    DTO (Data Transfer Object) for menu item API responses.

    This is a PYDANTIC MODEL - it defines the API contract for menu items.
    It lives in the interfaces layer (NOT domain layer).

    WHY SEPARATE FROM MenuItem ENTITY?
    - Separation of Concerns: API contracts ≠ business logic
    - Framework Independence: domain has no Pydantic dependency
    - API Evolution: can change API format without touching domain
    - Flexibility: API might flatten/reshape domain data

    DTO vs ENTITY - Key Differences:
    ┌─────────────────────┬──────────────────────┬──────────────────────┐
    │ Aspect              │ MenuItem (Entity)    │ MenuItemResponse (DTO)│
    ├─────────────────────┼──────────────────────┼──────────────────────┤
    │ Layer               │ Domain               │ Interface            │
    │ Purpose             │ Business logic       │ API contract         │
    │ Base class          │ dataclass            │ Pydantic BaseModel   │
    │ Validation          │ Business rules       │ Format/type checking │
    │ Dependencies        │ None (pure Python)   │ Pydantic, FastAPI    │
    │ Mutability          │ Immutable (frozen)   │ Immutable (config)   │
    │ Where used          │ Use cases, repos     │ API routes, clients  │
    └─────────────────────┴──────────────────────┴──────────────────────┘

    Real-world analogy: Think of MenuItem as the recipe in the kitchen (domain),
    and MenuItemResponse as the menu handed to customers (API).
    The recipe has detailed instructions (business logic),
    the menu has formatted descriptions (API contract).

    WHEN TO USE THIS:
    - Returning data from GET /menu/items
    - Returning data from GET /menu/items/{id}
    - Any API endpoint that sends menu item data to clients

    CONVERSION:
    In routers, we convert domain entities to DTOs:
    entity = MenuItem(...)  # Domain entity from use case
    response = MenuItemResponse(  # Convert to DTO for API
        id=entity.id,
        name=entity.name,
        ...
    )
    """

    # Unique identifier for this menu item
    # Example: "item-001" or "espresso-latte"
    id: str

    # Display name shown in menu
    # Example: "Espresso", "Cappuccino"
    name: str

    # Brief description for customers
    # Example: "Strong Italian coffee"
    description: str

    # Price with exactly 2 decimal places
    # Field(decimal_places=2) tells Pydantic to validate decimal precision
    # Example: Decimal("2.50")
    price: Decimal = Field(decimal_places=2)

    # Category this item belongs to
    # Example: "coffee", "pastry"
    category: str

    # Whether item is currently available
    # Example: True (can order), False (out of stock)
    available: bool

    @field_serializer("price")
    def serialize_price(self, price: Decimal, _info) -> float:
        """
        Convert Decimal price to float for JSON serialization.

        WHY THIS IS NEEDED:
        - JSON doesn't have a Decimal type (only number)
        - Decimal("2.50") → needs to become 2.5 in JSON
        - Pydantic field_serializer handles this conversion

        Args:
            price (Decimal): The Decimal price from the model
            _info: Serialization context (unused, but required by Pydantic)

        Returns:
            float: The price as a float for JSON
        """
        # Convert Decimal to float for JSON compatibility
        # Decimal("2.50") → 2.5
        return float(price)

    # Note: Pydantic v2 automatically handles validation:
    # - id must be a string
    # - price must be a Decimal with 2 decimal places
    # - available must be a boolean
    # We don't need to write validation code!

    # Example JSON output:
    # {
    #   "id": "item-001",
    #   "name": "Espresso",
    #   "description": "Strong Italian coffee",
    #   "price": 2.50,
    #   "category": "coffee",
    #   "available": true
    # }
