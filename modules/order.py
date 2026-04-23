# ─────────────────────────────────────────────────────────────────────────────
# order.py — Order Management + Stripe Payment
# ─────────────────────────────────────────────────────────────────────────────
#
# WHY THIS FILE EXISTS:
# Handles the checkout flow:
# 1. Create order from cart
# 2. Process payment via Stripe
# 3. Save order details
# 4. Return order confirmation
#
# STRIPE TEST MODE:
# Use sk_test_... key for testing
# No real money charged in test mode!
# Use card: 4242 4242 4242 4242
#           Any future date, any CVV
# ─────────────────────────────────────────────────────────────────────────────

import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")

# ── ORDER STATUSES ────────────────────────────────────────────────────────────
STATUS_PENDING   = "pending"
STATUS_PAID      = "paid"
STATUS_PREPARING = "preparing"
STATUS_READY     = "ready"
STATUS_DELIVERED = "delivered"
STATUS_CANCELLED = "cancelled"


def create_order(cart: dict, user_name: str,
                 delivery_address: str, phone: str) -> dict:
    """
    Creates an order from cart.

    Input:  cart dict + user details
    Output: order dict with unique ID
    """

    order_id = f"FM{datetime.now().strftime('%Y%m%d%H%M%S')}"

    return {
        "order_id":        order_id,
        "user_name":       user_name,
        "phone":           phone,
        "delivery_address":delivery_address,
        "restaurant":      cart.get("restaurant_name", "Restaurant"),
        "items":           cart["items"],
        "total_price":     cart["total_price"],
        "total_calories":  cart["total_calories"],
        "total_protein":   cart["total_protein"],
        "total_carbs":     cart["total_carbs"],
        "total_fat":       cart["total_fat"],
        "status":          STATUS_PENDING,
        "created_at":      datetime.now().isoformat(),
        "payment_status":  "unpaid",
    }


def process_payment_stripe(order: dict) -> dict:
    """
    Processes payment using Stripe.

    WHY Stripe:
    Most trusted payment gateway
    Works in India (Razorpay is better for India but Stripe for demo)
    Test mode = no real money charged

    Returns updated order with payment status.
    """

    if not STRIPE_SECRET_KEY:
        return {
            **order,
            "payment_status": "failed",
            "error": "STRIPE_SECRET_KEY not found in .env"
        }

    if not STRIPE_SECRET_KEY.startswith("sk_"):
        return {
            **order,
            "payment_status": "failed",
            "error": "Invalid Stripe key format"
        }

    try:
        import stripe
        stripe.api_key = STRIPE_SECRET_KEY

        # WHY amount * 100:
        # Stripe uses smallest currency unit
        # ₹120 = 12000 paise
        amount_paise = int(order["total_price"] * 100)

        # Create payment intent
        # WHY payment intent:
        # Modern Stripe flow
        # Handles all payment methods
        # Supports 3D secure automatically
        intent = stripe.PaymentIntent.create(
            amount=amount_paise,
            currency="inr",
            metadata={
                "order_id":   order["order_id"],
                "user_name":  order["user_name"],
                "restaurant": order["restaurant"],
            },
            description=f"FoodMood Order {order['order_id']}"
        )

        return {
            **order,
            "payment_status":   "intent_created",
            "payment_intent_id": intent.id,
            "client_secret":    intent.client_secret,
            "status":           STATUS_PAID,
        }

    except Exception as e:
        return {
            **order,
            "payment_status": "failed",
            "error":          str(e),
        }


def simulate_payment(order: dict) -> dict:
    """
    Simulates payment WITHOUT Stripe.
    Used when Stripe key not available.

    WHY simulate:
    For demo/testing purposes
    Shows full ordering flow without real payment
    """

    return {
        **order,
        "payment_status":    "simulated",
        "payment_intent_id": f"sim_{order['order_id']}",
        "status":            STATUS_PAID,
        "paid_at":           datetime.now().isoformat(),
    }


def process_order(cart: dict, user_name: str,
                  delivery_address: str, phone: str,
                  use_stripe: bool = True) -> dict:
    """
    Complete order processing flow.

    Step 1: Create order from cart
    Step 2: Process payment
    Step 3: Return confirmed order

    WHY combined function:
    app.py calls this one function
    Handles all logic internally
    Clean separation of concerns
    """

    # Step 1: Create order
    order = create_order(cart, user_name, delivery_address, phone)

    # Step 2: Process payment
    if use_stripe and STRIPE_SECRET_KEY:
        order = process_payment_stripe(order)
    else:
        # Simulate payment for demo
        order = simulate_payment(order)

    return order


def format_order_confirmation(order: dict) -> str:
    """Formats order confirmation message."""

    status_emoji = {
        STATUS_PENDING:   "⏳",
        STATUS_PAID:      "✅",
        STATUS_PREPARING: "👨‍🍳",
        STATUS_READY:     "🎉",
        STATUS_DELIVERED: "🏠",
        STATUS_CANCELLED: "❌",
    }

    emoji = status_emoji.get(order["status"], "📦")

    items_text = "\n".join([
        f"  {i['image']} {i['name']} x{i['quantity']} — ₹{i['subtotal_price']}"
        for i in order["items"]
    ])

    return (
        f"{emoji} Order Confirmed!\n"
        f"Order ID: {order['order_id']}\n"
        f"Restaurant: {order['restaurant']}\n\n"
        f"Items:\n{items_text}\n\n"
        f"Total: ₹{order['total_price']}\n"
        f"Calories: {order['total_calories']} kcal\n"
        f"Protein: {order['total_protein']}g\n\n"
        f"Delivering to: {order['delivery_address']}\n"
        f"Status: {order['status'].upper()}"
    )