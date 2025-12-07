"""
Configuration module for OpenCafe application.

This module manages database connection settings and other configuration values.
In production, these values should be loaded from environment variables.
"""

import os  # Used to read environment variables

# Database connection URL
# Format: "dialect+driver://username:password@host:port/database"
# For SQLite: "sqlite:///filename.db" (three slashes for relative path)
DATABASE_URL = os.getenv(
    "DATABASE_URL",  # Environment variable name
    "sqlite:///opencafe.db"  # Default value: SQLite database file in current directory
)

# Note: To switch to PostgreSQL, set DATABASE_URL environment variable:
# Example (SQLAlchemy 2.x + psycopg2 driver):
# export DATABASE_URL="postgresql+psycopg2://user:password@localhost:5432/opencafe"
# Or with psycopg3 driver:
# export DATABASE_URL="postgresql+psycopg://user:password@localhost:5432/opencafe"
