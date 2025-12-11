"""
SQLAlchemy implementation of OrderRepository.

This is the most complex repository because it handles AGGREGATES.
An Order contains OrderItems - they must be saved/loaded together.
"""

# Import typing for type hints
from typing import Optional

# Import Decimal for price calculations
from decimal import Decimal

# Import Session for database operations
from sqlalchemy.orm import Session

# Import domain entities and repository interface
from domain.entities.order import Order, OrderItem, OrderStatus
from domain.repositories.order_repository import OrderRepository

# Import SQLAlchemy models
from infrastructure.persistence.sqlalchemy_models import OrderModel, OrderItemModel


class SQLAlchemyOrderRepository(OrderRepository):
    """
    Database-backed implementation of OrderRepository.

    HANDLING AGGREGATES:
    Order is an aggregate root that contains OrderItems.
    When saving/loading orders, we must handle both tables:
    - orders table (parent)
    - order_items table (children)

    WHY COMPLEX?
    - Must maintain relationship between Order and OrderItems
    - Must handle creation and updates correctly
    - Must convert between models and entities in both directions

    Real-world analogy:
    - Order = kitchen ticket
    - OrderItems = individual lines on the ticket
    - Can't have a line without a ticket, can't save ticket without lines
    - Must save/load them together as one unit
    """

    def __init__(self, session: Session):
        """
        Initialize repository with database session.

        Args:
            session: SQLAlchemy Session for database operations
        """
        # Store session for all database operations
        self._session = session

    def save_order(self, order: Order) -> None:
        """
        Save order to database (create or update).

        This method implements UPSERT logic:
        - If order ID exists in database, update it
        - If order ID doesn't exist, create new row

        HANDLING THE AGGREGATE:
        1. Check if order exists in database
        2. If exists: delete old order_items, will recreate
        3. Convert Order entity to OrderModel
        4. Convert each OrderItem to OrderItemModel
        5. Add models to session
        6. Commit transaction to database

        Args:
            order: Order entity to save
        """
        # Check if order already exists in database
        # Query for existing order with this ID
        existing_order = self._session.query(OrderModel).filter(
            OrderModel.id == order.id
        ).first()

        # If order exists, we'll update it
        # Delete existing order items first (simpler than updating each one)
        if existing_order is not None:
            # Delete all old order items for this order
            # We'll recreate them from the entity
            self._session.query(OrderItemModel).filter(
                OrderItemModel.order_id == order.id
            ).delete()
            # Remove existing order model (will recreate)
            self._session.delete(existing_order)

        # Convert Order entity to OrderModel (database model)
        db_order = self._entity_to_model(order)

        # Add order to session (marks for INSERT)
        # Session will insert into orders table on commit
        self._session.add(db_order)

        # Commit transaction - saves to database
        # Writes both OrderModel and all OrderItemModels
        # All-or-nothing: if commit fails, nothing is saved
        self._session.commit()

    def get_order_by_id(self, order_id: str) -> Optional[Order]:
        """
        Retrieve order from database by ID.

        LOADING THE AGGREGATE:
        1. Query orders table for matching ID
        2. SQLAlchemy automatically loads related order_items (relationship)
        3. Convert OrderModel and OrderItemModels to entities
        4. Return complete Order entity

        Args:
            order_id: Unique identifier for order

        Returns:
            Order if found, None if not found
        """
        # Query database for order with this ID
        # .first() returns OrderModel or None
        db_order = self._session.query(OrderModel).filter(
            OrderModel.id == order_id
        ).first()

        # Return None if order not found
        if db_order is None:
            return None

        # Convert database models to domain entity
        # This handles both Order and its OrderItems
        return self._model_to_entity(db_order)

    def get_open_order_for_table(self, table_id: str) -> Optional[Order]:
        """
        Get any open order for a specific table.

        An "open" order is one that is NOT completed yet.
        This checks for orders in PENDING or CONFIRMED status.

        This implements a BUSINESS RULE: only one open order per table.
        Before creating a new order, check if table already has an active order.

        Args:
            table_id: ID of the table to check

        Returns:
            Order if table has an open order, None if table is available

        SQL equivalent:
        SELECT * FROM orders
        WHERE table_id = ? AND status IN ('pending', 'confirmed')
        LIMIT 1
        """
        # Query for orders matching this table
        # Filter for non-completed statuses (pending or confirmed)
        # .first() returns first match or None
        db_order = self._session.query(OrderModel).filter(
            OrderModel.table_id == table_id,  # Match table
            OrderModel.status.in_([  # Status is one of these
                OrderStatus.PENDING.value,  # "pending"
                OrderStatus.CONFIRMED.value,  # "confirmed"
            ])
        ).first()

        # Return None if no open order found
        if db_order is None:
            return None

        # Convert database model to domain entity
        return self._model_to_entity(db_order)

    def _model_to_entity(self, model: OrderModel) -> Order:
        """
        Convert database models to Order entity.

        This is DATABASE → DOMAIN conversion.
        Converts OrderModel + OrderItemModels → Order + OrderItems.

        Args:
            model: OrderModel from database (includes related OrderItemModels)

        Returns:
            Order: Complete domain entity with all items
        """
        # Convert each OrderItemModel to OrderItem entity
        # model.items is the relationship - list of OrderItemModel objects
        # SQLAlchemy loaded these automatically via relationship
        order_items = [
            OrderItem(
                menu_item_id=item.menu_item_id,  # Reference to menu item
                menu_item_name=item.menu_item_name,  # Snapshot: name
                unit_price=item.unit_price,  # Snapshot: price (already Decimal)
                quantity=item.quantity  # How many ordered
            )
            for item in model.items  # Loop through all order items
        ]

        # Create Order entity from OrderModel data
        return Order(
            id=model.id,  # Order ID
            table_id=model.table_id,  # Which table
            items=order_items,  # List of OrderItem entities we just created
            status=OrderStatus(model.status),  # Convert string → OrderStatus enum
            created_at=model.created_at  # Timestamp
        )

    def _entity_to_model(self, entity: Order) -> OrderModel:
        """
        Convert Order entity to database models.

        This is DOMAIN → DATABASE conversion.
        Converts Order + OrderItems → OrderModel + OrderItemModels.

        This method creates the SQLAlchemy models ready to be saved.

        Args:
            entity: Order domain entity

        Returns:
            OrderModel: Database model with related OrderItemModels
        """
        # Convert each OrderItem entity to OrderItemModel
        # Note: we don't set order_id yet - SQLAlchemy handles via relationship
        order_item_models = [
            OrderItemModel(
                # Don't set id - database auto-generates (autoincrement)
                # Don't set order_id - SQLAlchemy sets via relationship
                menu_item_id=item.menu_item_id,  # Reference
                menu_item_name=item.menu_item_name,  # Snapshot
                unit_price=item.unit_price,  # Snapshot (Decimal)
                quantity=item.quantity  # Quantity ordered
            )
            for item in entity.items  # Loop through domain OrderItems
        ]

        # Create OrderModel from Order entity
        db_order = OrderModel(
            id=entity.id,  # Order ID (set by use case)
            table_id=entity.table_id,  # Table reference
            status=entity.status.value,  # Convert OrderStatus enum → string value
            created_at=entity.created_at,  # Timestamp
            items=order_item_models  # Attach order items via relationship
        )

        # Return OrderModel ready to save
        # When we add this to session and commit:
        # - OrderModel inserts row into orders table
        # - Each OrderItemModel inserts row into order_items table
        # - SQLAlchemy sets order_id foreign key automatically
        return db_order
