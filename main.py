# Import the FastAPI class - main framework component
from fastapi import FastAPI

# Import our routers from the interfaces layer
# These routers handle different groups of endpoints
from interfaces.api.routers import health, menu, tables, orders


"""
Main FastAPI Application Entry Point

This is the composition root - where we assemble all the pieces:
- Create the FastAPI app
- Register routers
- Configure middleware (future)
- Set up app-level settings

COMPARE TO MODULE 0:
Module 0: Everything in one file (main.py)
- Routes defined here
- Database setup here
- Business logic mixed with HTTP handling

Module 1: Clean Architecture (this file)
- Routes organized in routers (health, menu)
- Business logic in use cases (application layer)
- Data access in repositories (infrastructure layer)
- This file just assembles the pieces

BENEFITS:
- Organized: each router handles related endpoints
- Testable: can test routes, use cases, and repositories independently
- Maintainable: easy to find and modify specific functionality
- Scalable: adding features means adding routers, not growing one huge file
"""


# Create the FastAPI application instance
# This is the main app that will run on the server
app = FastAPI(
    # Application metadata (shown in OpenAPI docs at /docs)
    title="OpenCafe Lite API",  # Name of your API
    description="Module 3: Persistence, Repositories & Migrations",  # Brief description
    version="0.4.0",  # Semantic versioning: 0.4.0 means Module 3

    # Future: you might add:
    # contact={"name": "API Support", "email": "support@opencafe.example"},
    # license_info={"name": "MIT"},
    # terms_of_service="https://opencafe.example/terms",
)


# Register routers with the application
# Each router handles a group of related endpoints

# Health check endpoints (GET /health)
# These routers are like plugins - they add their routes to the app
app.include_router(health.router)
# Now our app responds to GET /health (handled by health router)

# Menu endpoints (GET /menu/items)
app.include_router(menu.router)
# Now our app responds to GET /menu/items (handled by menu router)

# Table endpoints (GET /tables, GET /tables/{id})
app.include_router(tables.router)
# Now our app responds to table-related endpoints

# Order endpoints (POST /orders)
app.include_router(orders.router)
# Now our app responds to order-related endpoints

# Why use routers?
# - Organization: related endpoints grouped together
# - Separation of concerns: each router handles one area
# - Modularity: can enable/disable routers easily
# - Reusability: routers can be shared across apps
# - Clean: main.py stays small and focused


# Root endpoint - the "home page" of the API
@app.get("/")  # Decorator registers this function as handling GET /
def read_root():
    """
    Root endpoint - provides basic API information and navigation.

    This is a simple endpoint that helps users discover the API.
    Returns:
        dict: Welcome message and links to important endpoints

    Response Example:
        {
            "message": "Welcome to OpenCafe Lite!",
            "version": "0.2.0",
            "module": "Module 1: Clean Architecture",
            "endpoints": {
                "health": "/health",
                "menu": "/menu/items",
                "docs": "/docs"
            }
        }

    Why this endpoint?
    - Sanity check: if you visit http://localhost:8000/ you see something
    - Discovery: tells users where to find actual functionality
    - Docs: /docs link leads to interactive API documentation
    """

    # Return a dictionary with API information
    # FastAPI automatically converts this to JSON
    return {
        "message": "Welcome to OpenCafe Lite!",  # Friendly greeting
        "version": "0.4.0",  # Current version (matches app definition above)
        "module": "Module 3: Persistence, Repositories & Migrations",  # Which lesson this implements
        "endpoints": {  # Directory of available endpoints
            "health": "/health",  # Health check endpoint
            "menu": "/menu/items",  # Menu listing endpoint
            "tables": "/tables",  # Table listing endpoint
            "create_order": "POST /orders",  # Create order endpoint
            "get_table": "/tables/{table_id}",  # Get specific table
            "docs": "/docs"  # Auto-generated interactive documentation
        }
        # Future: might add
        # "status": "operational",
        # "environment": "development",
        # "uptime": calculate_uptime()
    }


# Note: We removed the database setup and health check from here
# They now live in health.router (interfaces/api/routers/health.py)
# This makes main.py much cleaner and focused

# Note: We removed the business logic from here
# It now lives in use cases (application/use_cases/)
# This separates HTTP concerns from business logic

# Note: We removed direct database queries from here
# They now live in repositories (infrastructure/persistence/)
# This separates data access from HTTP and business logic

# This file is now SMALL and FOCUSED - just app setup and router registration
# That's the goal of Clean Architecture!


# How to run this:
# 1. Activate virtual environment: source .venv/bin/activate
# 2. Run with uvicorn: uvicorn main:app --reload
# 3. Visit http://localhost:8000 for root endpoint
# 4. Visit http://localhost:8000/docs for interactive docs
# 5. Visit http://localhost:8000/menu/items for menu listing

# In production, you'd run with:
# uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
