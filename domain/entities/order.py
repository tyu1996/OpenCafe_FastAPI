# Import dataclass decorator for creating data classes easily
from dataclasses import dataclass

# Import datetime for tracking when orders are created
from datetime import datetime

# Import Decimal for precise money calculations (never use float for money!)
from decimal import Decimal

# Import Enum for creating constrained value sets (like order statuses)
from enum import Enum

# Import List for type hints indicating a list of items
from typing import List


class OrderStatus(Enum):
    """
    OrderStatus enum represents the lifecycle stages of an order.

    WHAT IS AN ENUM?
    - An enumeration is a set of named constants
    - Like a dropdown menu - only specific values are allowed
    - Python won't let you use invalid values like "INVALID_STATUS"

    WHY USE ENUM INSTEAD OF STRINGS?
    - Type safety: typos are caught at runtime
    - Autocomplete: IDEs can suggest valid values
    - Clear contract: readers know exactly what values are possible
    - Easy refactoring: changing a status name updates everywhere

    Real-world analogy: Order statuses are like stages in a restaurant kitchen ticket.
    PENDING → customer placed order, waiting for kitchen confirmation
    CONFIRMED → kitchen received and accepted the order
    PREPARING → chef is actively cooking the items
    READY → food is cooked and waiting for pickup/delivery
    COMPLETED → order delivered to customer, transaction finished
    """

    # Order has been placed but not yet confirmed by kitchen/staff
    # This is the initial state when a customer submits an order
    PENDING = "pending"

    # Order has been confirmed and will be prepared
    # Kitchen or staff have acknowledged the order
    CONFIRMED = "confirmed"

    # Order is actively being prepared in the kitchen
    # Chef is cooking the items
    PREPARING = "preparing"

    # Order is ready for pickup or delivery
    # Food is cooked and waiting
    READY = "ready"

    # Order has been delivered/picked up and completed
    # Final state - transaction is done
    COMPLETED = "completed"

    # Note: In a real system, you might also have:
    # CANCELLED, REFUNDED, FAILED
    # We keep it simple for learning purposes


@dataclass(frozen=True)  # frozen=True makes this IMMUTABLE (cannot change after creation)
class OrderItem:
    """
    OrderItem represents a single item within an order.

    This is a VALUE OBJECT - it has no identity, only values matter.
    Two OrderItems with the same values are considered identical.

    IMMUTABLE (frozen=True) - Why?
    - Once an order item is added to an order, it shouldn't change
    - Historical integrity: if menu prices change, old orders show original price
    - Thread-safe: immutable objects can be safely shared
    - Predictable: can't accidentally modify order history

    SNAPSHOT PATTERN - Key Teaching Point!
    Notice we store menu_item_name and unit_price, not just menu_item_id.
    This is DENORMALIZATION - intentionally duplicating data.

    Why duplicate data?
    - Historical accuracy: if "Espresso" is renamed to "Espresso Shot", old orders still show "Espresso"
    - Price history: if price changes from $2.50 to $3.00, old orders show original $2.50
    - Independence: orders don't break if menu items are deleted
    - Query efficiency: no need to join with menu table to display orders

    Real-world analogy: Think of this like items printed on a paper receipt.
    Once printed, the receipt doesn't change if the restaurant updates its menu.
    """

    # ID of the menu item (reference to MenuItem entity)
    # Used to link back to current menu (but order doesn't depend on it)
    menu_item_id: str

    # Snapshot of the menu item name at order time
    # Example: "Espresso", "Cappuccino", "Croissant"
    # Captured so orders show what customer actually ordered, even if name changes later
    menu_item_name: str

    # Snapshot of the price at order time
    # Example: Decimal("2.50") for $2.50
    # Captured so we bill the price customer saw when ordering, not current price
    unit_price: Decimal

    # How many of this item the customer wants
    # Example: 2 espressos, 3 croissants
    # Must be positive (can't order negative or zero items)
    quantity: int

    @property
    def subtotal(self) -> Decimal:
        """
        Calculate the subtotal for this order item.

        WHAT IS A PROPERTY?
        - Looks like an attribute but is actually a computed method
        - Access it like item.subtotal (no parentheses)
        - Calculated on-demand from other attributes
        - Not stored in the object (derived value)

        Why computed instead of stored?
        - Single source of truth: subtotal is always unit_price × quantity
        - Can't get out of sync (no way to set subtotal to wrong value)
        - Saves memory: don't store what we can calculate
        - Consistency: formula is defined once, used everywhere

        Formula: price per item × number of items
        Example: $2.50 per espresso × 2 espressos = $5.00 subtotal

        Returns:
            Decimal: The subtotal (unit_price × quantity)
        """
        # Multiply unit price by quantity to get line total
        # Use Decimal for precise money math (no floating point errors)
        return self.unit_price * Decimal(self.quantity)

    def __post_init__(self):
        """
        Validation logic for OrderItem.

        Enforces business rules that must ALWAYS be true.
        Called automatically after dataclass __init__.
        """

        # Business Rule #1: Quantity must be positive
        # Can't order zero or negative items
        # Real-world: "I want -2 coffees" makes no sense
        if self.quantity <= 0:
            raise ValueError("Order item quantity must be greater than zero")

        # Business Rule #2: Unit price cannot be negative
        # Even free items have price = 0, not negative
        # Negative price would mean paying the customer
        if self.unit_price < Decimal("0"):
            raise ValueError("Order item price cannot be negative")

        # Business Rule #3: Menu item name cannot be empty
        # Need to know what was ordered for display and kitchen prep
        if not self.menu_item_name.strip():
            raise ValueError("Order item name cannot be empty")


@dataclass  # NOT frozen - Orders are MUTABLE (status changes over time)
class Order:
    """
    Order represents a customer's complete order at a table.

    This is an AGGREGATE ROOT - a cluster of related objects treated as a single unit.
    Order is the "root" that controls access to OrderItems.

    MUTABLE (NOT frozen) - Why?
    - Order status changes over its lifecycle (PENDING → CONFIRMED → PREPARING → READY → COMPLETED)
    - Orders represent processes that evolve over time
    - The order ID and creation time stay constant, but status changes

    AGGREGATE ROOT - What does this mean?
    - External code interacts with Order, not directly with OrderItems
    - Order enforces invariants (business rules) about its OrderItems
    - Order is the consistency boundary - all items in an order are consistent
    - Changes to OrderItems must go through Order's methods

    Real-world analogy: Think of Order like a physical order ticket in a restaurant.
    The ticket lists all items (OrderItems), shows the table, and has a status
    (waiting, cooking, ready). The status changes, but the items don't.
    """

    # Unique identifier for this order (like "order-001" or UUID)
    id: str

    # ID of the table this order belongs to (reference to Table entity)
    # Links the order to a physical location in the cafe
    table_id: str

    # List of items in this order
    # Each OrderItem is immutable, but the list itself could change
    # (though in this simple version, we don't add items after creation)
    items: List[OrderItem]

    # Current status of the order (one of the OrderStatus enum values)
    # Changes as order progresses through its lifecycle
    status: OrderStatus

    # When this order was created (timestamp)
    # Useful for tracking order age, historical reports, etc.
    created_at: datetime

    @property
    def total(self) -> Decimal:
        """
        Calculate the total price for the entire order.

        This is a DERIVED VALUE - computed from order items, not stored.

        Why computed?
        - Single source of truth: total is always sum of item subtotals
        - Can't get out of sync (if items change, total auto-updates)
        - Consistency: calculation is centralized in one place

        Formula: sum of all item subtotals
        Example: Espresso ($5.00) + Croissant ($3.50) = $8.50 total

        Returns:
            Decimal: The order total (sum of all OrderItem.subtotal values)
        """
        # Sum the subtotals of all items in this order
        # sum() adds up all values from the generator expression
        # (item.subtotal for item in self.items) generates each item's subtotal
        return sum((item.subtotal for item in self.items), start=Decimal("0"))
        # start=Decimal("0") ensures we return Decimal("0") for empty orders
        # and keeps the sum as Decimal type (not int)

    def __post_init__(self):
        """
        Validation logic for Order.

        Enforces business rules (invariants) that define what makes a valid order.
        These rules must be true when the order is created and throughout its lifetime.
        """

        # Business Rule #1: Orders must have at least one item
        # Can't place an empty order - what would the kitchen prepare?
        # Real-world: you can't submit a blank order ticket
        if not self.items:
            raise ValueError("Order must contain at least one item")

        # Note: We could add more validation:
        # - Maximum number of items per order
        # - Validate status is a valid OrderStatus
        # - Validate table_id exists (but that's repository's job)
        # - Validate total doesn't exceed some maximum
        # Keep it simple for now
