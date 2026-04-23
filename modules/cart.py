# ─────────────────────────────────────────────────────────────────────────────
# cart.py — Shopping Cart Management
# ─────────────────────────────────────────────────────────────────────────────
#
# WHY THIS FILE EXISTS:
# User adds items from restaurant menu
# Cart tracks items, quantities, totals
# Shows calories + price together
# ─────────────────────────────────────────────────────────────────────────────


def create_cart() -> dict:
    """Creates an empty cart."""
    return {
        "items":           [],
        "restaurant_name": "",
        "total_price":     0,
        "total_calories":  0,
        "total_protein":   0,
        "total_carbs":     0,
        "total_fat":       0,
    }


def add_to_cart(cart: dict, item: dict, quantity: int = 1) -> dict:
    """
    Adds an item to cart.

    WHY check existing items:
    If same item added twice → increase quantity
    Don't create duplicate entries
    """

    # Check if item already in cart
    for cart_item in cart["items"]:
        if cart_item["id"] == item["id"]:
            cart_item["quantity"] += quantity
            cart_item["subtotal_price"]    = cart_item["price"] * cart_item["quantity"]
            cart_item["subtotal_calories"] = cart_item["calories"] * cart_item["quantity"]
            return recalculate_totals(cart)

    # New item — add to cart
    cart["items"].append({
        "id":               item["id"],
        "name":             item["name"],
        "price":            item["price"],
        "calories":         item["calories"],
        "protein":          item["protein"],
        "carbs":            item["carbs"],
        "fat":              item["fat"],
        "image":            item.get("image", "🍽️"),
        "quantity":         quantity,
        "subtotal_price":   item["price"]    * quantity,
        "subtotal_calories":item["calories"] * quantity,
    })

    return recalculate_totals(cart)


def remove_from_cart(cart: dict, item_id: str) -> dict:
    """Removes an item from cart."""
    cart["items"] = [i for i in cart["items"] if i["id"] != item_id]
    return recalculate_totals(cart)


def update_quantity(cart: dict, item_id: str, quantity: int) -> dict:
    """Updates quantity of an item in cart."""
    if quantity <= 0:
        return remove_from_cart(cart, item_id)

    for item in cart["items"]:
        if item["id"] == item_id:
            item["quantity"]          = quantity
            item["subtotal_price"]    = item["price"]    * quantity
            item["subtotal_calories"] = item["calories"] * quantity

    return recalculate_totals(cart)


def recalculate_totals(cart: dict) -> dict:
    """
    Recalculates all totals after any cart change.

    WHY separate function:
    Called after every add/remove/update
    Single source of truth for totals
    """
    cart["total_price"]    = sum(i["subtotal_price"]    for i in cart["items"])
    cart["total_calories"] = sum(i["subtotal_calories"] for i in cart["items"])
    cart["total_protein"]  = sum(i["protein"] * i["quantity"] for i in cart["items"])
    cart["total_carbs"]    = sum(i["carbs"]   * i["quantity"] for i in cart["items"])
    cart["total_fat"]      = sum(i["fat"]     * i["quantity"] for i in cart["items"])
    return cart


def clear_cart(cart: dict) -> dict:
    """Clears all items from cart."""
    return create_cart()


def get_cart_meal_dict(cart: dict) -> dict:
    """
    Converts cart to FoodMood meal dict format.

    WHY this function:
    After order placed → automatically log to daily log!
    This converts cart format to our meal tracking format
    Same format as calorie_calculator output
    """
    return {
        "items":          [{"food": i["name"], "grams": 0} for i in cart["items"]],
        "total_calories": cart["total_calories"],
        "total_protein":  cart["total_protein"],
        "total_carbs":    cart["total_carbs"],
        "total_fat":      cart["total_fat"],
        "total_sugar":    0,
        "total_sodium":   0,
        "total_fiber":    0,
        "skipped_foods":  [],
        "source":         "order",
    }