# Import the FastAPI class - this is the main building block for creating APIs
from fastapi import FastAPI

# Import SQLAlchemy components for database operations
# create_engine: creates a connection to the database
# text: allows us to write raw SQL queries safely
from sqlalchemy import create_engine, text

# Step 1: Create the FastAPI application instance
# This is like turning on your API server
# Think of it as opening a restaurant - this creates the building
app = FastAPI(
    title="OpenCafe Lite API",              # Name shown in the API documentation
    description="Module 0: Smoke Test",     # Brief description of what this API does
    version="0.1.0"                         # Version number (we start at 0.1.0)
)

# Step 2: Set up database connection
# SQLite is a file-based database - no server needed
# The database will be stored in a file called 'test.db' in the same folder
DATABASE_URL = "sqlite:///./test.db"

# Create the database engine (the connection manager)
# connect_args={"check_same_thread": False} allows FastAPI to use SQLite safely
# Without this, SQLite would only work in single-threaded mode
engine = create_engine(
    DATABASE_URL,                           # Where to find/create the database
    connect_args={"check_same_thread": False}  # Allow multi-threaded access
)

# Step 3: Define a health check endpoint
# The @app.get() decorator means "when someone visits /health, run this function"
# Decorators add special behavior to functions - here it registers an API endpoint
@app.get("/health")
def health_check():
    """
    Health check endpoint - confirms the API is running and database works.

    Returns:
        dict: A JSON response with status and database connection info
    """

    # Try to connect to the database and run a test query
    try:
        # Create a connection to the database
        # 'with' ensures the connection closes automatically when done
        with engine.connect() as connection:
            # Execute a simple SQL query: SELECT 1
            # This is the simplest query possible - just returns the number 1
            # It proves the database connection works
            result = connection.execute(text("SELECT 1"))

            # Fetch the result to confirm the query actually ran
            # fetchone() gets one row from the result
            result.fetchone()

        # If we got here, database connection worked!
        db_status = "connected"

    except Exception as e:
        # If anything went wrong (database file locked, permissions issue, etc.)
        # Store the error message so we can debug
        db_status = f"error: {str(e)}"

    # Return a dictionary - FastAPI automatically converts this to JSON
    # JSON is the standard format for API responses
    return {
        "status": "healthy",                    # API is running
        "message": "OpenCafe API is ready!",    # Friendly message
        "database": db_status                   # Database connection result
    }

# Step 4: Root endpoint - the homepage of your API
@app.get("/")
def read_root():
    """
    Root endpoint - returns a welcome message.

    When someone visits http://localhost:8000/ they see this response.
    This is like the front door of your API.

    Returns:
        dict: Welcome message with information about the API
    """

    # Return helpful information about where to find API documentation
    return {
        "message": "Welcome to OpenCafe Lite!",
        "docs": "Visit /docs for interactive API documentation",
        "health": "Visit /health to check if the API is running properly"
    }
