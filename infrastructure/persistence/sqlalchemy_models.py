"""
SQLAlchemy ORM Models for OpenCafe database.

These models define the database schema. They are SEPARATE from domain entities.
Domain entities = business logic (pure Python, no framework dependencies)
ORM models = database structure (SQLAlchemy, tied to infrastructure)

Think of ORM models as the "translator" between Python objects and database tables.
"""

# Import Decimal for precise money storage in database
from decimal import Decimal

# Import Column, Integer, String, etc. - these define table columns
# Import ForeignKey for relationships between tables
# Import Numeric for storing decimal numbers (prices)
# Import declarative_base to create base class for all models
# Import relationship for navigating between related objects
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import declarative_base, relationship

# Create base class for all ORM models
# All model classes will inherit from Base
# Base tracks metadata about tables (schema info)
Base = declarative_base()


class MenuCategoryModel(Base):
    """
    Database model for menu_categories table.

    Maps to MenuCategory domain entity.
    Stores category information like "Coffee Drinks", "Pastries", etc.
    """

    # Table name in the database
    # SQLAlchemy will create a table with this name
    __tablename__ = "menu_categories"

    # Primary key column - unique identifier for each category
    # String type allows IDs like "cat-001" or UUIDs
    # primary_key=True means this column uniquely identifies rows
    id = Column(String, primary_key=True)

    # Category name displayed to users
    # nullable=False means this column cannot be NULL (required field)
    name = Column(String, nullable=False)

    # Category description - what items belong here
    # nullable=False means description is required
    description = Column(String, nullable=False)

    # Relationship: One category has many menu items
    # back_populates creates bidirectional relationship
    # Allows: category.items to get all items in this category
    # cascade="all, delete-orphan" means: delete items when category is deleted
    items = relationship("MenuItemModel", back_populates="category_rel", cascade="all, delete-orphan")


class MenuItemModel(Base):
    """
    Database model for menu_items table.

    Maps to MenuItem domain entity.
    Stores items on the menu like "Espresso", "Croissant", etc.
    """

    # Table name in the database
    __tablename__ = "menu_items"

    # Primary key - unique identifier for each menu item
    id = Column(String, primary_key=True)

    # Item name shown to customers
    name = Column(String, nullable=False)

    # Item description explaining what it is
    description = Column(String, nullable=False)

    # Price stored as Numeric(10, 2)
    # 10 = total digits, 2 = digits after decimal point
    # Example: 12345678.90 (max value)
    # Why Numeric instead of Float? Precise money calculations (no rounding errors)
    price = Column(Numeric(10, 2), nullable=False)

    # Foreign key linking to menu_categories table
    # Every menu item belongs to exactly one category
    # ForeignKey creates database constraint (can't link to non-existent category)
    category_id = Column(String, ForeignKey("menu_categories.id"), nullable=False)

    # Whether item is currently available for ordering
    # Boolean stored as 0/1 in SQLite, true/false in PostgreSQL
    # default=True means new items are available unless specified otherwise
    available = Column(Integer, nullable=False, default=1)  # SQLite uses 1 for True, 0 for False

    # Relationship: Many items belong to one category
    # back_populates="items" links to MenuCategoryModel.items
    # Allows: item.category_rel to get the category object
    category_rel = relationship("MenuCategoryModel", back_populates="items")


class TableModel(Base):
    """
    Database model for tables table.

    Maps to Table domain entity.
    Stores physical seating tables in the cafe.
    """

    # Table name in the database
    # Note: "tables" is a reserved word in some databases, but SQLite/Postgres handle it
    __tablename__ = "tables"

    # Primary key - unique identifier for each table
    id = Column(String, primary_key=True)

    # Table number shown to customers (like "Table 5")
    # Stored as integer for sorting and display
    number = Column(Integer, nullable=False)

    # Maximum people who can sit at this table
    capacity = Column(Integer, nullable=False)

    # Physical location description (like "window", "patio")
    location = Column(String, nullable=False)

    # Relationship: One table can have many orders (over time)
    # back_populates creates bidirectional link
    # Allows: table.orders to get all orders for this table
    orders = relationship("OrderModel", back_populates="table_rel")


class OrderModel(Base):
    """
    Database model for orders table.

    Maps to Order domain entity.
    Stores customer orders placed at tables.
    """

    # Table name in the database
    __tablename__ = "orders"

    # Primary key - unique identifier for each order
    id = Column(String, primary_key=True)

    # Foreign key linking to tables table
    # Every order is placed at exactly one table
    table_id = Column(String, ForeignKey("tables.id"), nullable=False)

    # Order status stored as string value (like "pending", "confirmed")
    # We store OrderStatus.value (the string), not the enum object
    # Database stores: "pending", "confirmed", "preparing", "ready", "completed"
    status = Column(String, nullable=False)

    # Timestamp when order was created
    # DateTime type stores full date and time
    # Used for tracking order age, history, analytics
    created_at = Column(DateTime, nullable=False)

    # Relationship: Many orders belong to one table
    # Allows: order.table_rel to get the Table object
    table_rel = relationship("TableModel", back_populates="orders")

    # Relationship: One order has many order items
    # cascade="all, delete-orphan" means: delete items when order is deleted
    # Allows: order.items to get all items in this order
    items = relationship("OrderItemModel", back_populates="order_rel", cascade="all, delete-orphan")


class OrderItemModel(Base):
    """
    Database model for order_items table.

    Maps to OrderItem value object.
    Stores individual items within an order.

    KEY TEACHING POINT - SNAPSHOT PATTERN:
    Notice menu_item_id is NOT a foreign key!
    We store name and price directly (denormalization).

    Why snapshot data instead of just storing menu_item_id with foreign key?
    1. Historical accuracy: If menu item is renamed, old orders show original name
    2. Price integrity: If price changes, old orders show price customer paid
    3. Independence: Orders don't break if menu items are deleted
    4. Query efficiency: No join needed to display order details

    Real-world analogy: Like a printed receipt. Once printed, it doesn't change
    when the restaurant updates its menu or prices.
    """

    # Table name in the database
    __tablename__ = "order_items"

    # Primary key - unique identifier for each order item
    # Auto-generated integer ID (simpler than composite key)
    # autoincrement=True means database assigns next number automatically
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign key linking to orders table
    # Every order item belongs to exactly one order
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)

    # SNAPSHOT: Menu item ID stored for reference
    # This is NOT a foreign key! It's just a string we remember
    # Links back to current menu (if item still exists)
    # But order doesn't depend on menu item existing
    menu_item_id = Column(String, nullable=False)

    # SNAPSHOT: Menu item name at time order was placed
    # Captured so we remember what customer ordered, even if name changes
    # Example: "Espresso" stored when order placed, even if later renamed to "Espresso Shot"
    menu_item_name = Column(String, nullable=False)

    # SNAPSHOT: Price at time order was placed
    # Numeric(10, 2) for precise money storage
    # Captured so we charge the price customer saw when ordering
    # Example: If espresso was $2.50 when ordered, we bill $2.50 even if price is now $3.00
    unit_price = Column(Numeric(10, 2), nullable=False)

    # Quantity of this item ordered
    # How many of this item customer wants
    quantity = Column(Integer, nullable=False)

    # Relationship: Many order items belong to one order
    # Allows: order_item.order_rel to get the Order object
    order_rel = relationship("OrderModel", back_populates="items")
