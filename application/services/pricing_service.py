# Import Decimal for precise money calculations
from decimal import Decimal

# Import dataclass for creating data transfer objects
from dataclasses import dataclass

# Import List for type hints
from typing import List, Optional

# Import domain entities
from domain.entities.order import Order, OrderItem


@dataclass
class LineItemPrice:
    """
    Breakdown of a single line item's pricing.

    Shows how we calculated the subtotal for one item.
    This provides transparency: customer can see the math.

    Real-world analogy: Line on a receipt showing:
    "2x Espresso @ $2.50 each = $5.00"
    """
    # Name of the menu item (from snapshot)
    item_name: str

    # How many ordered
    quantity: int

    # Price per item (from snapshot)
    unit_price: Decimal

    # Total for this line (unit_price × quantity)
    # This is pre-discount (raw subtotal)
    subtotal: Decimal


@dataclass
class OrderPricing:
    """
    Complete pricing breakdown for an order.

    This is what we return from the pricing engine.
    Shows all calculations step-by-step so customer understands the bill.

    Real-world analogy: Itemized receipt showing:
    - Each item's subtotal
    - Sum of all items (subtotal)
    - Discount applied (if any)
    - Final total
    """
    # Breakdown of each line item
    # List of LineItemPrice objects, one per OrderItem
    line_items: List[LineItemPrice]

    # Sum of all line item subtotals (before discount)
    # This is: item1.subtotal + item2.subtotal + ...
    subtotal: Decimal

    # Discount amount applied (0 if no discount)
    # Always positive: $5 discount, not -$5
    discount_amount: Decimal

    # Discount description (why discount was applied)
    # Examples: "10% off all orders", "Member discount", None if no discount
    discount_reason: Optional[str]

    # Final total after discount
    # Formula: subtotal - discount_amount
    # This is what customer pays
    total: Decimal


class PricingService:
    """
    Service for calculating order prices with optional discounts.

    This is a DOMAIN SERVICE - it contains business logic that doesn't
    belong to a single entity but operates on domain concepts.

    WHY A SEPARATE SERVICE?
    - Order entity calculates total, but doesn't handle discounts
    - Discount rules are business logic (10% off, member discounts, promos)
    - Centralizes pricing calculations in one place
    - Easy to test pricing logic separately
    - Can enhance with complex rules without changing Order entity

    MODULE 5 SCOPE (Simple):
    - Calculate line item subtotals
    - Sum to order subtotal
    - Apply ONE simple discount rule (optional flat percentage)
    - Return itemized breakdown

    MODULE 7A EXPANSION (Advanced):
    - Member-based discounts
    - Time-based promotions (happy hour)
    - Item-specific discounts
    - Multiple discount rules with priority

    Real-world analogy: Think of this as the "price calculator" at checkout.
    It looks at your cart (order), calculates each item, applies any discounts
    (coupon, membership), and shows you the itemized receipt.

    TEACHING NOTE:
    This demonstrates the SERVICE LAYER pattern - when business logic
    doesn't fit naturally into an entity, create a service.
    """

    def __init__(self, default_discount_percentage: Decimal = Decimal("0")):
        """
        Initialize the pricing service.

        Args:
            default_discount_percentage: Percentage discount to apply (0-100)
                                        Example: Decimal("10") for 10% off
                                        Default: Decimal("0") for no discount

        WHY CONFIGURABLE DISCOUNT?
        - Café might run a promotion: "10% off all orders today"
        - Can be injected via dependency injection
        - Easy to test with different discount rates
        - Matches real business: discounts are configuration, not code

        Example configurations:
        - PricingService() → no discount
        - PricingService(Decimal("10")) → 10% off everything
        - PricingService(Decimal("15")) → 15% off (special event)
        """
        # Store discount percentage for applying to orders
        self._default_discount_percentage = default_discount_percentage

        # Validate discount is reasonable (0-100)
        # Can't have negative discount (charging more?)
        # Can't have >100% discount (paying customers?)
        if not (Decimal("0") <= default_discount_percentage <= Decimal("100")):
            raise ValueError("Discount percentage must be between 0 and 100")

    def calculate_order_pricing(self, order: Order) -> OrderPricing:
        """
        Calculate complete pricing breakdown for an order.

        This is the MAIN METHOD of the pricing service.
        Given an order, return itemized pricing with discounts.

        Args:
            order (Order): The order to calculate pricing for
                          Must have items list populated

        Returns:
            OrderPricing: Complete breakdown with line items, subtotal, discount, total

        Algorithm (5 steps):
        1. Calculate each line item subtotal (unit_price × quantity)
        2. Sum all line items to get order subtotal
        3. Calculate discount amount (subtotal × discount_percentage)
        4. Calculate final total (subtotal - discount_amount)
        5. Return OrderPricing with all details

        Example:
        Order with:
        - 2x Espresso @ $2.50 = $5.00
        - 1x Croissant @ $3.50 = $3.50
        Subtotal: $8.50
        10% discount: $0.85
        Total: $7.65
        """
        # STEP 1: Calculate line item pricing
        # Create LineItemPrice for each OrderItem
        line_items = [
            LineItemPrice(
                item_name=item.menu_item_name,  # From snapshot
                quantity=item.quantity,  # How many
                unit_price=item.unit_price,  # Price per item (from snapshot)
                subtotal=item.subtotal  # Calculated property: unit_price × quantity
            )
            for item in order.items  # Loop through all items in order
        ]

        # STEP 2: Calculate order subtotal (sum of all line items)
        # This is the total BEFORE any discounts
        # order.total property already does this calculation, so we use it
        subtotal = order.total

        # STEP 3: Calculate discount amount
        # Formula: subtotal × (discount_percentage / 100)
        # Example: $100 × (10 / 100) = $100 × 0.10 = $10 discount
        discount_amount = subtotal * (self._default_discount_percentage / Decimal("100"))

        # Round to 2 decimal places (cents)
        # quantize ensures we have exactly 2 decimal places
        # Example: Decimal("1.5555") → Decimal("1.56")
        discount_amount = discount_amount.quantize(Decimal("0.01"))

        # STEP 4: Determine discount reason (for receipt display)
        # If discount was applied, explain why
        # If no discount, reason is None
        if self._default_discount_percentage > Decimal("0"):
            # Create human-readable reason
            # Example: "10% discount applied"
            discount_reason = f"{self._default_discount_percentage}% discount applied"
        else:
            # No discount, no reason
            discount_reason = None

        # STEP 5: Calculate final total
        # Formula: subtotal - discount_amount
        # Example: $8.50 - $0.85 = $7.65
        total = subtotal - discount_amount

        # STEP 6: Create and return OrderPricing breakdown
        return OrderPricing(
            line_items=line_items,  # Itemized list
            subtotal=subtotal,  # Total before discount
            discount_amount=discount_amount,  # How much saved
            discount_reason=discount_reason,  # Why discount applied
            total=total  # Final amount to pay
        )

    # WHAT WE LEARNED:
    # 1. Domain services handle business logic that spans multiple entities
    # 2. Pricing logic is separate from Order entity (single responsibility)
    # 3. Return structured data (OrderPricing) for transparency
    # 4. Use Decimal for all money calculations (never float!)
    # 5. Configuration via dependency injection (default_discount_percentage)
    # 6. Itemized breakdown helps customer understand the bill

    # MODULE 7A ENHANCEMENTS (Future):
    # In advanced module, this service might:
    # - Look up member ID and apply member discount
    # - Check current time and apply happy hour pricing
    # - Query promotions table for active deals
    # - Stack multiple discounts with priority rules
    # - Explain each discount in the breakdown
    #
    # For now (Module 5), we keep it simple: one flat discount percentage.
