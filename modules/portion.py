# Portion size assumptions in grams
# These are heuristic defaults for MVP (explainable & adjustable)

UNIT_TO_GRAMS = {
    "bowl": 150,
    "plate": 200,
    "cup": 120,
    "piece": 60,
    "pieces": 60,
    "unit": 100  # fallback when unit is unknown
}

# Food-specific overrides (per piece or per unit)
FOOD_UNIT_GRAMS = {
    "roti": 60,          # per piece
    "egg": 50,           # per egg
    "chicken": 150,      # per serving
    "paneer": 100,       # per serving
    "salad": 100,
    "rice": 150,
    "dal": 150
}


def estimate_portion(food, quantity, unit):
    """
    Estimate portion size in grams for a given food.
    Returns grams and an explanation string.
    """
    food = food.lower()
    unit = unit.lower()

    # Determine base grams
    if food in FOOD_UNIT_GRAMS:
        base_grams = FOOD_UNIT_GRAMS[food]
        source = f"food-specific assumption ({base_grams}g per {unit})"
    else:
        base_grams = UNIT_TO_GRAMS.get(unit, UNIT_TO_GRAMS["unit"])
        source = f"unit-based assumption ({base_grams}g per {unit})"

    total_grams = base_grams * quantity

    explanation = (
        f"Assumed {base_grams}g per {unit} for {food}. "
        f"Quantity: {quantity}. Total: {total_grams}g."
    )

    return total_grams, explanation
