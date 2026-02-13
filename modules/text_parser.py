import re

# Default unit if not specified
DEFAULT_UNIT = "unit"

# Word-based quantities
WORD_TO_NUMBER = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5
}

# Known food keywords (for detection in text)
KNOWN_FOODS = ["rice", "roti", "dal", "salad", "chicken", "egg", "eggs", "paneer", "boiled egg"]

# Map text mentions to nutrition CSV keys
FOOD_ALIASES = {
    "egg": "egg_boiled",
    "eggs": "egg_boiled",
    "boiled egg": "egg_boiled",
    "chicken": "chicken_grilled",
    "rice": "rice",
    "roti": "roti",
    "dal": "dal",
    "salad": "salad",
    "paneer": "paneer"
}

# Known units
KNOWN_UNITS = ["bowl", "plate", "piece", "pieces", "cup", "cups"]

def extract_food_items(text):
    """
    Extracts food items, quantities, and units from input text.
    Returns a list of dicts compatible with the calorie calculator.
    """
    text = text.lower()
    results = []

    for food in KNOWN_FOODS:
        # Regex to find food with optional numeric quantity
        pattern = r"(\d+)?\s*(?:{})".format(re.escape(food))
        matches = re.finditer(pattern, text)

        for m in matches:
            qty = m.group(1)
            quantity = int(qty) if qty else 1
            unit = DEFAULT_UNIT

            # Check for unit before or after food
            for u in KNOWN_UNITS:
                if f"{u} of {food}" in text or f"{food} {u}" in text:
                    unit = u
                    break

            # Map to nutrition database key
            key = FOOD_ALIASES.get(food)
            if key:
                results.append({
                    "food": key,
                    "quantity": quantity,
                    "unit": unit,
                    "confidence": 80  # Default confidence for text input
                })

    return results
