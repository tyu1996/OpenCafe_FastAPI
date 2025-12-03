# OpenCafe Lite API - Module 1: Clean Architecture

A FastAPI backend for a fictional café, built using Clean Architecture principles.

## What's New in Module 1

Module 1 transforms the flat Module 0 structure into a properly layered Clean Architecture:

- ✅ Four-layer architecture (domain, application, infrastructure, interface)
- ✅ Ports & adapters pattern
- ✅ Dependency injection
- ✅ Menu listing feature (first vertical slice)
- ✅ Comprehensive test suite (23 tests, <0.1s execution)

## Project Structure

```
code/
├── main.py                           # FastAPI app entry point
├── requirements.txt                  # Python dependencies
├── pytest.ini                        # Pytest configuration
│
├── domain/                           # Core business logic (zero dependencies)
│   ├── entities/
│   │   └── menu.py                  # MenuItem entity with validation
│   └── repositories/
│       └── menu_repository.py       # MenuRepository port (interface)
│
├── application/                      # Use cases and workflows
│   └── use_cases/
│       └── list_menu_items.py       # ListMenuItems use case
│
├── infrastructure/                   # External service implementations
│   └── persistence/
│       └── in_memory_menu_repository.py  # In-memory adapter
│
├── interfaces/                       # API layer (HTTP)
│   └── api/
│       ├── dependencies.py          # Dependency injection setup
│       └── routers/
│           ├── health.py            # Health check endpoint
│           └── menu.py              # Menu endpoints
│
└── tests/                            # Test suite
    ├── conftest.py                  # Shared test fixtures
    ├── unit/                        # Unit tests (fast, isolated)
    │   ├── domain/
    │   │   └── test_menu_entity.py
    │   └── application/
    │       └── test_list_menu_items.py
    └── integration/                 # Integration tests (full stack)
        └── test_menu_api.py
```

## Architecture Layers

### Layer 1: Domain (Core)

**What**: Pure business logic and entities
**Dependencies**: None
**Example**: `MenuItem` entity with validation rules

```python
@dataclass(frozen=True)
class MenuItem:
    id: str
    name: str
    price: Decimal
    # Business rule: prices can't be negative
```

### Layer 2: Application

**What**: Use cases that orchestrate business operations
**Dependencies**: Domain only
**Example**: `ListMenuItems` use case

```python
class ListMenuItems:
    def __init__(self, repository: MenuRepository):
        self._repository = repository

    def execute(self, only_available: bool = True):
        items = self._repository.list_all_items()
        if only_available:
            items = [item for item in items if item.available]
        return items
```

### Layer 3: Infrastructure

**What**: Implementations of external services
**Dependencies**: Implements domain ports
**Example**: `InMemoryMenuRepository` adapter

```python
class InMemoryMenuRepository(MenuRepository):
    def list_all_items(self):
        return list(self._items.values())
```

### Layer 4: Interface

**What**: HTTP API endpoints
**Dependencies**: Application and domain
**Example**: FastAPI routers

```python
@router.get("/menu/items")
def list_menu_items(use_case = Depends(...)):
    return use_case.execute()
```

## Installation & Setup

### 1. Activate Virtual Environment

**Mac/Linux**:
```bash
source ../.venv/bin/activate
```

**Windows**:
```bash
..\.venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Dependencies:
- `fastapi==0.115.0` - Web framework
- `uvicorn==0.32.0` - ASGI server
- `sqlalchemy==2.0.35` - Database toolkit
- `pytest==7.4.3` - Testing framework
- `pytest-asyncio==0.21.1` - Async test support
- `httpx==0.25.1` - HTTP client for testing

## Running the Application

### Start the Server

```bash
uvicorn main:app --reload
```

Server starts at: http://localhost:8000

The `--reload` flag automatically restarts the server when code changes.

### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Welcome message and API info |
| `/health` | GET | Health check (API + database status) |
| `/menu/items` | GET | List available menu items |
| `/menu/items?only_available=false` | GET | List all menu items (including unavailable) |
| `/docs` | GET | Interactive API documentation (Swagger UI) |
| `/redoc` | GET | Alternative API documentation (ReDoc) |

### Example API Calls

**Get available menu items**:
```bash
curl http://localhost:8000/menu/items
```

Response:
```json
[
  {
    "id": "item-001",
    "name": "Espresso",
    "description": "Strong Italian coffee",
    "price": 2.5,
    "category": "coffee",
    "available": true
  },
  ...
]
```

**Get all items including unavailable**:
```bash
curl http://localhost:8000/menu/items?only_available=false
```

**Check API health**:
```bash
curl http://localhost:8000/health
```

## Running Tests

### Run All Tests

```bash
pytest -v
```

Expected output:
```
============================= test session starts ==============================
...
tests/unit/domain/test_menu_entity.py::...           PASSED
tests/unit/application/test_list_menu_items.py::...  PASSED
tests/integration/test_menu_api.py::...              PASSED
======================== 23 passed in 0.04s ===============================
```

### Run Specific Test Suites

**Unit tests only** (domain + application):
```bash
pytest tests/unit/ -v
```

**Integration tests only**:
```bash
pytest tests/integration/ -v
```

**Domain tests only**:
```bash
pytest tests/unit/domain/ -v
```

### Test Coverage

- **7 domain tests**: Entity validation and immutability
- **6 application tests**: Use case logic with fake repositories
- **10 integration tests**: Full HTTP request/response cycle

All tests run in < 0.1 seconds!

## Development Workflow

### Adding a New Feature

Follow this pattern for new features:

1. **Domain**: Create entity with validation
   ```python
   # domain/entities/order.py
   @dataclass(frozen=True)
   class Order:
       id: str
       table_id: str
       # ... fields and validation
   ```

2. **Port**: Define interface
   ```python
   # domain/repositories/order_repository.py
   class OrderRepository(ABC):
       @abstractmethod
       def save(self, order: Order) -> None:
           pass
   ```

3. **Use Case**: Implement business operation
   ```python
   # application/use_cases/create_order.py
   class CreateOrder:
       def __init__(self, repository: OrderRepository):
           self._repository = repository

       def execute(self, order_data):
           # Business logic here
           pass
   ```

4. **Adapter**: Implement storage
   ```python
   # infrastructure/persistence/in_memory_order_repository.py
   class InMemoryOrderRepository(OrderRepository):
       def save(self, order: Order) -> None:
           self._orders[order.id] = order
   ```

5. **Router**: Add HTTP endpoint
   ```python
   # interfaces/api/routers/orders.py
   @router.post("/orders")
   def create_order(use_case = Depends(...)):
       return use_case.execute(...)
   ```

6. **Tests**: Add unit and integration tests

## Key Benefits of This Architecture

### Testability

```python
# Test business logic WITHOUT starting FastAPI or database!
def test_list_available_items():
    fake_repo = FakeMenuRepository([...])
    use_case = ListMenuItems(fake_repo)
    result = use_case.execute(only_available=True)
    assert all(item.available for item in result)
```

### Flexibility

```python
# Swap storage implementation by changing ONE line
# In dependencies.py:
_repository = InMemoryMenuRepository()  # Development
# _repository = SQLAlchemyMenuRepository()  # Production
```

### Independence

- Domain layer has ZERO FastAPI dependencies
- Business logic works in any context (API, CLI, background job)
- Database can change without touching business logic

### Maintainability

- Each layer has clear responsibility
- Easy to find code: "Where's the validation?" → domain
- Easy to test: isolated layers with clear interfaces

## Common Issues & Solutions

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'domain'`

**Solution**: Make sure you're in the `code/` directory and have `__init__.py` files in all package folders.

### Tests Not Found

**Problem**: `pytest` finds no tests

**Solution**: Make sure you're running pytest from the `code/` directory:
```bash
cd code/
pytest
```

### Server Won't Start

**Problem**: `Address already in use`

**Solution**: Port 8000 is already in use. Either:
- Stop the existing server (Ctrl+C)
- Use a different port: `uvicorn main:app --port 8001`

## Next Steps

After Module 1, you should be able to:

✅ Understand the four layers of Clean Architecture
✅ Create domain entities with validation
✅ Define ports (interfaces) and adapters (implementations)
✅ Write use cases that coordinate business logic
✅ Wire up FastAPI with dependency injection
✅ Test business logic without starting the server

**Continue to Module 2** to learn:
- Complete domain modeling (orders, tables, categories)
- Complex use cases with multiple entities
- DTOs vs domain entities
- Validation strategies

## Resources

- **Lesson File**: `../lessons/module-01-clean-architecture.md`
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Pytest Docs**: https://docs.pytest.org/
- **Clean Architecture Book**: Robert C. Martin

## Module Progression

- [x] **Module 0**: Pre-Course Setup & FastAPI Smoke Test
- [x] **Module 1**: Project Structure & Clean Architecture ← You are here
- [ ] **Module 2**: Domain Modeling, DTOs & Use Cases
- [ ] **Module 3**: Persistence, Repositories & Migrations
- [ ] **Module 4**: Menu & Table APIs (DB-Backed)
- [ ] **Module 5**: Orders, Pricing Engine & Transactions
- [ ] **Module 6**: Auth, Roles & Securing Endpoints

---

Built with ❤️ for learning Clean Architecture with FastAPI
