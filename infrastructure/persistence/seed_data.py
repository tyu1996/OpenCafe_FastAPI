"""
Seed script to populate database with sample data for OpenCafe.

Run this after migrations to add initial menu categories, items, and tables.
Makes it easy to test the API without manually creating data.

Usage:
    python -m infrastructure.persistence.seed_data
"""

# Import Decimal for precise price values
from decimal import Decimal

# Import database session factory
from infrastructure.persistence.database import SessionLocal

# Import SQLAlchemy models (database layer)
from infrastructure.persistence.sqlalchemy_models import (
    MenuCategoryModel,
    MenuItemModel,
    TableModel
)


def seed_database():
    """
    Populate database with sample data.

    This function is IDEMPOTENT - safe to run multiple times.
    It checks if data already exists before inserting.
    Won't create duplicates if you run it twice.

    WHAT IT CREATES:
    - 3 menu categories (Coffee, Pastries, Sandwiches)
    - 6 menu items (2 per category)
    - 4 tables (different sizes and locations)

    WHY SEED DATA?
    - Quick setup for development
    - Consistent test data across environments
    - Easy demo without manual data entry
    - Realistic examples for learning
    """
    # Create a database session
    # Session manages transaction and database connection
    db = SessionLocal()

    try:
        # Check if data already exists
        # Count existing categories in database
        # If categories exist, assume database is already seeded
        existing_categories = db.query(MenuCategoryModel).count()

        if existing_categories > 0:
            print("Database already has data. Skipping seed.")
            return

        print("Seeding database with sample data...")

        # ===== CATEGORIES =====
        # Create three menu categories
        # These organize menu items into logical groups

        coffee_category = MenuCategoryModel(
            id="cat-001",  # Unique ID
            name="Coffee Drinks",  # Display name
            description="Hot and cold coffee beverages"  # Description
        )

        pastries_category = MenuCategoryModel(
            id="cat-002",
            name="Pastries",
            description="Fresh baked goods and desserts"
        )

        sandwiches_category = MenuCategoryModel(
            id="cat-003",
            name="Sandwiches",
            description="Lunch sandwiches and wraps"
        )

        # Add categories to session
        # Session tracks these objects for insertion
        db.add(coffee_category)
        db.add(pastries_category)
        db.add(sandwiches_category)

        # ===== MENU ITEMS =====
        # Create menu items for each category
        # Items reference category via category_id foreign key

        # Coffee items
        espresso = MenuItemModel(
            id="item-001",
            name="Espresso",
            description="Strong Italian coffee",
            price=Decimal("2.50"),  # $2.50 - use Decimal for money
            category_id="cat-001",  # Links to Coffee Drinks category
            available=1  # 1 = available (SQLite uses int for boolean)
        )

        cappuccino = MenuItemModel(
            id="item-002",
            name="Cappuccino",
            description="Espresso with steamed milk foam",
            price=Decimal("3.50"),  # $3.50
            category_id="cat-001",
            available=1
        )

        # Pastry items
        croissant = MenuItemModel(
            id="item-003",
            name="Croissant",
            description="Buttery French pastry",
            price=Decimal("3.00"),  # $3.00
            category_id="cat-002",  # Links to Pastries category
            available=1
        )

        muffin = MenuItemModel(
            id="item-004",
            name="Blueberry Muffin",
            description="Fresh baked muffin with blueberries",
            price=Decimal("2.75"),  # $2.75
            category_id="cat-002",
            available=1
        )

        # Sandwich items
        club_sandwich = MenuItemModel(
            id="item-005",
            name="Club Sandwich",
            description="Triple-decker with turkey and bacon",
            price=Decimal("8.50"),  # $8.50
            category_id="cat-003",  # Links to Sandwiches category
            available=1
        )

        veggie_wrap = MenuItemModel(
            id="item-006",
            name="Veggie Wrap",
            description="Fresh vegetables in a whole wheat wrap",
            price=Decimal("7.00"),  # $7.00
            category_id="cat-003",
            available=1
        )

        # Add all menu items to session
        db.add(espresso)
        db.add(cappuccino)
        db.add(croissant)
        db.add(muffin)
        db.add(club_sandwich)
        db.add(veggie_wrap)

        # ===== TABLES =====
        # Create seating tables for the cafe
        # Different sizes and locations

        table_1 = TableModel(
            id="table-001",
            number=1,  # Table 1
            capacity=2,  # Seats 2 people
            location="window"  # By the window
        )

        table_2 = TableModel(
            id="table-002",
            number=2,
            capacity=4,  # Seats 4 people
            location="main-room"  # Main dining area
        )

        table_3 = TableModel(
            id="table-003",
            number=3,
            capacity=4,
            location="patio"  # Outside patio
        )

        table_4 = TableModel(
            id="table-004",
            number=4,
            capacity=6,  # Seats 6 people (large table)
            location="main-room"
        )

        # Add all tables to session
        db.add(table_1)
        db.add(table_2)
        db.add(table_3)
        db.add(table_4)

        # Commit transaction - save all data to database
        # This writes everything to the database at once
        # If any error occurs, nothing is saved (transaction rolls back)
        db.commit()

        print("✓ Created 3 categories")
        print("✓ Created 6 menu items")
        print("✓ Created 4 tables")
        print("Database seeded successfully!")

    except Exception as e:
        # If anything goes wrong, rollback transaction
        # This undoes all changes since last commit
        db.rollback()
        print(f"Error seeding database: {e}")
        raise  # Re-raise exception so caller knows it failed

    finally:
        # Always close session when done
        # Releases database connection back to pool
        # Runs even if exception occurred
        db.close()


# This block runs when file is executed directly
# Allows running: python -m infrastructure.persistence.seed_data
if __name__ == "__main__":
    seed_database()
