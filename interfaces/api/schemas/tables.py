# Import Pydantic BaseModel for API validation and serialization
from pydantic import BaseModel


class TableResponse(BaseModel):
    """
    DTO (Data Transfer Object) for table API responses.

    This is a PYDANTIC MODEL that defines the API contract for tables.
    It's the interface layer representation of table data.

    WHY SEPARATE FROM Table ENTITY?
    - Layer separation: API contracts live in interfaces/, not domain/
    - Framework independence: domain doesn't depend on Pydantic
    - API flexibility: can reshape data for API without changing domain

    DTO vs ENTITY - For Tables:
    ┌─────────────────────┬──────────────────────┬──────────────────────┐
    │ Aspect              │ Table (Entity)       │ TableResponse (DTO)  │
    ├─────────────────────┼──────────────────────┼──────────────────────┤
    │ Layer               │ Domain               │ Interface            │
    │ Purpose             │ Business rules       │ API contract         │
    │ Base class          │ dataclass            │ Pydantic BaseModel   │
    │ Validation          │ Business (capacity>0)│ Type checking        │
    │ Fields              │ Same 4 fields        │ Same 4 fields        │
    └─────────────────────┴──────────────────────┴──────────────────────┘

    In this case, the DTO looks very similar to the entity.
    That's okay! Not all DTOs are drastically different from entities.
    The important thing is the SEPARATION, not the difference.

    Real-world analogy: Think of Table entity as the physical table tag
    (with all its properties), and TableResponse as the table info shown
    on a seating chart displayed to customers.

    WHEN TO USE THIS:
    - Returning data from GET /tables
    - Returning data from GET /tables/{id}
    - Any API endpoint that sends table data to clients
    """

    # Unique identifier for the table
    # Example: "table-001"
    id: str

    # Table number displayed to customers and staff
    # Example: 5 (as in "Table 5")
    number: int

    # Maximum number of people who can sit at this table
    # Example: 4 (seats 4 people)
    capacity: int

    # Physical location of the table
    # Example: "window", "patio", "main-room"
    location: str

    # Note: Pydantic automatically validates:
    # - id is a string
    # - number is an integer
    # - capacity is an integer
    # - location is a string
    #
    # But Pydantic does NOT validate business rules like "capacity > 0"
    # That's the domain entity's job!

    # Example JSON output:
    # {
    #   "id": "table-001",
    #   "number": 1,
    #   "capacity": 2,
    #   "location": "window"
    # }
