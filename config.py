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
# export DATABASE_URL="postgresql://user:password@localhost:5432/opencafe"
