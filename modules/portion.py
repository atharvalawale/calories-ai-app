def estimate_portion(detected_foods):
    """
    Input:
    [{'food': 'salad', 'quantity': 1, 'unit': 'unit'}]

    Output:
    [{'food': 'salad', 'grams': 100}]
    """

    PORTION_DB = {
        "rice": 200,
        "pizza": 150,
        "salad": 100,
        "roti": 50,
        "dal": 180,
        "egg_boiled": 60,       # FIXED: match parser output & CSV
        "chicken_grilled": 200, # FIXED: match parser output & CSV
        "paneer": 120
    }

    portions = []

    for item in detected_foods:
        food = item["food"]
        qty = item.get("quantity", 1)

        base = PORTION_DB.get(food, 100)
        total = base * qty

        portions.append({
            "food": food,
            "grams": total   # IMPORTANT → only number, not tuple
        })

    return portions
