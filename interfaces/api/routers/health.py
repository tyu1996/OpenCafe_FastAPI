# Import FastAPI router - allows us to organize endpoints into modules
from fastapi import APIRouter

# Import SQLAlchemy for database health check
from sqlalchemy import create_engine, text


"""
Health Check Router

This module provides health check endpoints for monitoring the API.

WHY HEALTH CHECKS?
- Monitoring: external systems can check if API is alive
- Load balancers: determine if instance should receive traffic
- Debugging: quick way to verify API and dependencies work
- Operations: alerting systems can monitor health endpoint

This is a ROUTER, not the main app:
- Routers are modular pieces that can be included in the main app
- Each router handles a related group of endpoints
- Makes code organized and easier to maintain
"""


# Create an APIRouter instance
# This is like a mini FastAPI app that handles a subset of endpoints
router = APIRouter(
    # Prefix: all routes in this router start with /health
    # Example: if we add @router.get("/check"), it becomes /health/check
    prefix="/health",
    # Tags: used for grouping in OpenAPI docs
    # All endpoints in this router appear under "health" section in /docs
    tags=["health"]
)


# Set up database connection for health check
# This is the same database setup as in Module 0's main.py
DATABASE_URL = "sqlite:///./test.db"  # SQLite file in current directory
engine = create_engine(
    DATABASE_URL,  # Where to find the database
    connect_args={"check_same_thread": False}  # Allow multi-threaded access
)
# Note: In production, DATABASE_URL would come from environment variables
# Example: DATABASE_URL = os.getenv("DATABASE_URL")


@router.get("")  # Empty string means just /health (no additional path)
def health_check():
    """
    Health check endpoint - confirms API is running and database is accessible.

    This endpoint should:
    - Respond quickly (< 1 second)
    - Return 200 OK if healthy
    - Include status of critical dependencies (database)
    - Not require authentication (public endpoint)

    Returns:
        dict: Health status information including database connectivity

    Response example:
        {
            "status": "healthy",
            "message": "OpenCafe API is ready!",
            "database": "connected"
        }

    Why this endpoint?
    - Load balancers call this to check if instance is healthy
    - Monitoring systems call this to track uptime
    - Developers call this to verify deployment worked
    - It's a simple smoke test: if this works, basic infrastructure is OK
    """

    # Try to check database connectivity
    try:
        # Open a database connection
        # 'with' ensures connection closes automatically (even if error occurs)
        with engine.connect() as connection:
            # Execute the simplest possible query: SELECT 1
            # This just returns the number 1, proving the database responds
            # Any more complex query would be slower and test more than we need
            result = connection.execute(text("SELECT 1"))

            # Fetch the result to confirm the query actually executed
            # If database is broken, this line would raise an exception
            result.fetchone()

        # If we got here, database connection worked!
        db_status = "connected"

    except Exception as e:
        # Something went wrong with database connection
        # Catch the exception so API doesn't crash
        # Store error message for debugging
        db_status = f"error: {str(e)}"
        # Note: In production, you might also log this error
        # import logging
        # logging.error(f"Database health check failed: {e}")

    # Return health status as JSON
    # FastAPI automatically converts this dict to JSON
    return {
        "status": "healthy",  # API is running (we're executing code)
        "message": "OpenCafe API is ready!",  # Friendly message
        "database": db_status,  # Database connectivity status
        # Future: could add more checks here
        # "redis": redis_status,
        # "external_api": external_api_status,
        # "version": "0.2.0",
        # "uptime": calculate_uptime()
    }

    # Note: If database is down, we still return 200 OK
    # This is a design choice:
    # - Some people prefer returning 503 Service Unavailable if dependencies are down
    # - We return 200 but include error details in response body
    # - This way load balancers know API is alive, but details show what's broken
    # - Choose the approach that matches your infrastructure needs
