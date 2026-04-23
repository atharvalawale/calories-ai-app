# ─────────────────────────────────────────────────────────────────────────────
# menu.py — Menu Database with Nutrition Info
# ─────────────────────────────────────────────────────────────────────────────
#
# WHY THIS FILE EXISTS:
# TomTom gives us restaurant names but NOT menu items
# We need our own menu database with:
# - Menu items per restaurant
# - Price per item
# - Macros per item (using our Recipe Engine!)
#
# HOW IT WORKS:
# - Sample menus for common restaurant types
# - Each item has ingredients → Recipe Engine calculates macros
# - Provider can add their own menu later (Phase 4)
# ─────────────────────────────────────────────────────────────────────────────

# ── SAMPLE MENU DATABASE ──────────────────────────────────────────────────────
# WHY hardcoded sample menus:
# Phase 3 = basic ordering demo
# Phase 4 = providers add real menus
# This gets us working ordering system NOW!

SAMPLE_MENUS = {
    "indian": [
        {
            "id":          "dal_rice_01",
            "name":        "Dal Rice",
            "description": "Yellow dal with steamed rice",
            "price":       120,
            "calories":    450,
            "protein":     18,
            "carbs":       75,
            "fat":         8,
            "category":    "Main Course",
            "veg":         True,
            "image":       "🍛",
        },
        {
            "id":          "paneer_butter_masala_01",
            "name":        "Paneer Butter Masala",
            "description": "Paneer in rich tomato gravy with butter",
            "price":       220,
            "calories":    380,
            "protein":     22,
            "carbs":       18,
            "fat":         28,
            "category":    "Main Course",
            "veg":         True,
            "image":       "🧀",
        },
        {
            "id":          "chicken_biryani_01",
            "name":        "Chicken Biryani",
            "description": "Fragrant basmati rice with spiced chicken",
            "price":       280,
            "calories":    620,
            "protein":     38,
            "carbs":       72,
            "fat":         18,
            "category":    "Main Course",
            "veg":         False,
            "image":       "🍗",
        },
        {
            "id":          "roti_sabzi_01",
            "name":        "Roti + Sabzi",
            "description": "2 rotis with seasonal vegetable curry",
            "price":       90,
            "calories":    280,
            "protein":     8,
            "carbs":       48,
            "fat":         6,
            "category":    "Main Course",
            "veg":         True,
            "image":       "🫓",
        },
        {
            "id":          "masala_chai_01",
            "name":        "Masala Chai",
            "description": "Indian spiced tea with milk",
            "price":       30,
            "calories":    80,
            "protein":     3,
            "carbs":       12,
            "fat":         2,
            "category":    "Beverages",
            "veg":         True,
            "image":       "☕",
        },
    ],
    "fast food": [
        {
            "id":          "veg_burger_01",
            "name":        "Veg Burger",
            "description": "Crispy veg patty with lettuce and sauce",
            "price":       150,
            "calories":    420,
            "protein":     12,
            "carbs":       52,
            "fat":         18,
            "category":    "Burgers",
            "veg":         True,
            "image":       "🍔",
        },
        {
            "id":          "chicken_burger_01",
            "name":        "Chicken Burger",
            "description": "Grilled chicken patty with veggies",
            "price":       180,
            "calories":    480,
            "protein":     28,
            "carbs":       48,
            "fat":         20,
            "category":    "Burgers",
            "veg":         False,
            "image":       "🍔",
        },
        {
            "id":          "french_fries_01",
            "name":        "French Fries",
            "description": "Crispy golden fries with dip",
            "price":       80,
            "calories":    320,
            "protein":     4,
            "carbs":       42,
            "fat":         16,
            "category":    "Sides",
            "veg":         True,
            "image":       "🍟",
        },
        {
            "id":          "cold_drink_01",
            "name":        "Cold Drink",
            "description": "Chilled soft drink 300ml",
            "price":       50,
            "calories":    140,
            "protein":     0,
            "carbs":       36,
            "fat":         0,
            "category":    "Beverages",
            "veg":         True,
            "image":       "🥤",
        },
    ],
    "american": [
        {
            "id":          "grilled_chicken_01",
            "name":        "Grilled Chicken",
            "description": "Herb-marinated grilled chicken breast",
            "price":       320,
            "calories":    280,
            "protein":     42,
            "carbs":       4,
            "fat":         12,
            "category":    "Main Course",
            "veg":         False,
            "image":       "🍗",
        },
        {
            "id":          "caesar_salad_01",
            "name":        "Caesar Salad",
            "description": "Romaine lettuce with caesar dressing",
            "price":       220,
            "calories":    180,
            "protein":     8,
            "carbs":       12,
            "fat":         14,
            "category":    "Salads",
            "veg":         True,
            "image":       "🥗",
        },
        {
            "id":          "pasta_01",
            "name":        "Pasta Arrabiata",
            "description": "Penne pasta in spicy tomato sauce",
            "price":       280,
            "calories":    420,
            "protein":     14,
            "carbs":       68,
            "fat":         10,
            "category":    "Pasta",
            "veg":         True,
            "image":       "🍝",
        },
    ],
    "default": [
        {
            "id":          "veg_thali_01",
            "name":        "Veg Thali",
            "description": "Complete veg meal with dal, sabzi, roti, rice",
            "price":       160,
            "calories":    650,
            "protein":     22,
            "carbs":       98,
            "fat":         18,
            "category":    "Thali",
            "veg":         True,
            "image":       "🍱",
        },
        {
            "id":          "chicken_thali_01",
            "name":        "Chicken Thali",
            "description": "Complete meal with chicken curry, roti, rice",
            "price":       200,
            "calories":    780,
            "protein":     45,
            "carbs":       88,
            "fat":         22,
            "category":    "Thali",
            "veg":         False,
            "image":       "🍱",
        },
        {
            "id":          "fruit_juice_01",
            "name":        "Fresh Fruit Juice",
            "description": "Seasonal fresh fruit juice 300ml",
            "price":       80,
            "calories":    120,
            "protein":     1,
            "carbs":       28,
            "fat":         0,
            "category":    "Beverages",
            "veg":         True,
            "image":       "🧃",
        },
    ]
}


def get_menu_for_restaurant(cuisine_type: str) -> list:
    """
    Returns menu items for a restaurant based on cuisine type.

    WHY cuisine based menus:
    We don't have real menus for every restaurant
    So we show sample menus based on cuisine type
    Phase 4 = real providers add their own menus
    """
    cuisine = cuisine_type.lower().strip()

    # Find best matching menu
    for key in SAMPLE_MENUS:
        if key in cuisine or cuisine in key:
            return SAMPLE_MENUS[key]

    # Default menu if no match
    return SAMPLE_MENUS["default"]


def get_item_by_id(item_id: str) -> dict | None:
    """Finds a menu item by its ID across all menus."""
    for menu in SAMPLE_MENUS.values():
        for item in menu:
            if item["id"] == item_id:
                return item
    return None