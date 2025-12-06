"""
Database session management for OpenCafe.

This module handles:
1. Database engine creation (connection to database)
2. Session factory (creates database sessions)
3. Dependency injection for FastAPI (provides sessions to endpoints)
4. Table creation helper (for initial setup)

WHAT IS A SESSION?
Think of a session like a "shopping cart" for database operations:
- Add items (queries, inserts, updates) to the cart
- When ready, "checkout" with commit() - all changes save together
- If something goes wrong, "empty cart" with rollback() - nothing saves
- When done shopping, close() the cart and return it

Why sessions instead of direct SQL?
- Transaction safety: All changes happen together or not at all
- Connection management: Sessions handle database connections automatically
- Object tracking: Session tracks which objects changed
- Clean abstraction: Work with Python objects, not SQL strings
"""

# Import config to get DATABASE_URL
from config import DATABASE_URL

# Import create_engine - creates connection to database
# create_engine manages connection pool, handles reconnection, etc.
from sqlalchemy import create_engine

# Import sessionmaker - factory for creating Session objects
# Session is the main interface for talking to database
from sqlalchemy.orm import sessionmaker, Session

# Import Base to access metadata (table definitions)
from infrastructure.persistence.sqlalchemy_models import Base


# Create database engine (connection to database)
# engine is the "low-level" database connection
# It manages connection pooling, reconnects, etc.
# connect_args: SQLite-specific setting for thread safety
# check_same_thread=False allows SQLite to be used with FastAPI (async framework)
# For PostgreSQL, this parameter is not needed
engine = create_engine(
    DATABASE_URL,  # Database connection string from config
    connect_args={"check_same_thread": False},  # SQLite-specific: allow multi-threading
    echo=False  # Set to True to see all SQL queries (useful for debugging)
)

# Create SessionLocal class (factory for creating sessions)
# sessionmaker is a factory that generates Session objects
# Each Session is independent and manages its own transaction
# autocommit=False: We manually call commit() (safer, more control)
# autoflush=False: We manually call flush() (better performance)
# bind=engine: Sessions use this engine to connect to database
SessionLocal = sessionmaker(
    autocommit=False,  # Require explicit commit() - safer than auto-committing
    autoflush=False,   # Require explicit flush() - better performance control
    bind=engine        # Use the engine we created above
)


def get_db_session() -> Session:
    """
    Dependency function for FastAPI routes.

    Provides a database session to endpoint handlers.
    Used with FastAPI's Depends() for dependency injection.

    HOW IT WORKS:
    1. Create a new session when endpoint is called
    2. Yield the session to the endpoint handler (pause here)
    3. Endpoint uses session to query/modify database
    4. After endpoint finishes (success or error), resume here
    5. Close the session to release database connection

    Why use yield instead of return?
    - yield pauses execution and resumes after endpoint finishes
    - Code after yield runs even if endpoint raises exception
    - Guaranteed cleanup: session always closes, even on errors
    - This pattern is called "context manager" or "dependency with cleanup"

    Example usage in FastAPI route:
    ```python
    @router.get("/items")
    def list_items(db: Session = Depends(get_db_session)):
        # db is automatically created and injected
        items = db.query(MenuItemModel).all()
        return items
        # After returning, session automatically closes
    ```

    Yields:
        Session: A database session for the request
    """
    # Create new session for this request
    # Each request gets its own isolated session
    db = SessionLocal()

    try:
        # Yield session to the endpoint handler
        # Execution pauses here while endpoint runs
        yield db
    finally:
        # This runs AFTER endpoint finishes (success or exception)
        # Close session to release database connection back to pool
        # This cleanup happens even if endpoint raised an error
        db.close()


def create_tables():
    """
    Create all tables defined in SQLAlchemy models.

    WHEN TO USE:
    - Initial database setup (before first run)
    - Testing (create schema in test database)

    WHEN NOT TO USE:
    - Production (use Alembic migrations instead)
    - After changing models (use migrations for schema changes)

    WHY NOT IN PRODUCTION?
    - create_all() only creates NEW tables, doesn't modify existing
    - Can't handle schema changes (add column, rename table, etc.)
    - No version control or rollback capability
    - Alembic migrations solve these problems

    Real-world analogy:
    create_all() is like building a house from scratch.
    Migrations are like renovation blueprints (add room, move wall, etc.)

    This function is useful for:
    - Quick local development setup
    - Test database initialization
    - Learning and experimentation
    """
    # Base.metadata contains info about all tables (from all models)
    # create_all() creates tables that don't exist yet
    # Existing tables are not modified or dropped
    Base.metadata.create_all(bind=engine)
