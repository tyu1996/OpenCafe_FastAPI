# Import FastAPI components
from fastapi import APIRouter, Depends, HTTPException, status

# Import type hints
from typing import List

# Import use cases from application layer
from application.use_cases.get_table import GetTable
from application.use_cases.list_tables import ListTables  # MODULE 4: New use case

# Import DTOs from schemas directory
from interfaces.api.schemas.tables import TableResponse

# Import dependency functions
from interfaces.api.dependencies import (
    get_get_table_use_case,
    get_list_tables_use_case,  # MODULE 4: New dependency
)


"""
Tables Router - API endpoints for table operations

This is the INTERFACE LAYER:
- Handles HTTP concerns (routes, status codes)
- Converts between domain entities and DTOs
- Thin layer: delegates to use cases

SIMPLICITY:
This router is simpler than orders router because:
- Tables are read-only in Module 2 (no create/update/delete)
- Simple entity-to-DTO conversion (same fields)
- Straightforward use cases
"""

# Create the router for table-related endpoints
router = APIRouter(
    prefix="/tables",  # All routes start with /tables
    tags=["tables"]    # Groups endpoints in OpenAPI docs under "tables"
)


@router.get("", response_model=List[TableResponse])
def list_tables(
    # Query parameter for filtering by area (MODULE 4 ENHANCEMENT)
    area: str | None = None,  # Filter by location (optional)

    # Dependency injection - FastAPI provides configured use case
    use_case: ListTables = Depends(get_list_tables_use_case),
):
    """
    List all tables in the cafe with optional area filtering.

    MODULE 4 ENHANCEMENT: Added area filter parameter.

    This endpoint is useful for:
    - Showing seating options to customers
    - Staff viewing available tables
    - Order placement (choosing a table)
    - Filtering tables by location preference

    Query Parameters:
        area (str, optional): Filter tables by location.
                             Examples: "window", "patio", "main-room"
                             If not provided, returns all tables.

    Response example:
    [
        {
            "id": "table-001",
            "number": 1,
            "capacity": 2,
            "location": "window"
        },
        {
            "id": "table-002",
            "number": 2,
            "capacity": 4,
            "location": "main-room"
        },
        ...
    ]

    Example Requests:
        GET /tables
            -> Returns all tables

        GET /tables?area=window
            -> Returns only tables by the window

        GET /tables?area=patio
            -> Returns only outdoor patio tables

    HOW THIS WORKS (Module 4 - with use case):
    1. FastAPI injects ListTables use case via DI
    2. Use case calls repository with optional area filter
    3. Repository queries database with filter (if provided)
    4. We convert entities to DTOs (TableResponse)
    5. FastAPI serializes to JSON and returns HTTP 200
    """

    # Execute use case with optional area filter
    # The use case coordinates with repository to apply filtering
    tables = use_case.execute(area=area)

    # Convert Table entities → TableResponse DTOs
    response = [
        TableResponse(
            id=table.id,  # Copy from entity
            number=table.number,  # Copy from entity
            capacity=table.capacity,  # Copy from entity
            location=table.location,  # Copy from entity
        )
        for table in tables  # For each Table entity
    ]

    # Return DTOs (FastAPI serializes to JSON)
    return response


@router.get("/{table_id}", response_model=TableResponse)
def get_table(
    table_id: str,  # Path parameter from URL
    use_case: GetTable = Depends(get_get_table_use_case),  # Dependency injection
):
    """
    Get details of a specific table by ID.

    This endpoint is useful for:
    - Validating table exists before placing order
    - Showing table details to staff
    - Checking table capacity

    Path parameter:
        table_id: Unique identifier of the table (e.g., "table-001")

    Response example:
    {
        "id": "table-001",
        "number": 1,
        "capacity": 2,
        "location": "window"
    }

    Error responses:
    - 404 Not Found: Table with given ID doesn't exist

    HOW THIS WORKS:
    1. FastAPI extracts table_id from URL path
    2. FastAPI injects GetTable use case
    3. We execute use case with table_id
    4. Use case returns Optional[Table] (Table or None)
    5. If None, we raise HTTPException 404
    6. If found, we convert Table entity → TableResponse DTO
    7. FastAPI serializes to JSON and returns HTTP 200
    """

    # Execute use case with table_id parameter
    # Returns Optional[Table] - either a Table entity or None
    table = use_case.execute(table_id=table_id)

    # Handle not found case
    # If table is None, return 404 error
    if table is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table with ID '{table_id}' not found"
        )

    # Convert Table entity → TableResponse DTO
    # Table and TableResponse have same fields, so conversion is simple
    response = TableResponse(
        id=table.id,
        number=table.number,
        capacity=table.capacity,
        location=table.location,
    )

    # Return DTO (FastAPI serializes to JSON)
    return response


# Future endpoints we might add in Module 5:
#
# @router.get("/{table_id}/open-order", response_model=OrderResponse)
# def get_table_open_order(table_id: str):
#     """Get the currently open order for a table (if any)."""
#     # ...
#
# @router.get("/{table_id}/availability", response_model=TableAvailabilityResponse)
# def check_table_availability(table_id: str):
#     """Check if a table is currently available (no active orders)."""
#     # ...
#
# For Module 2, we keep it simple: just list and get.
