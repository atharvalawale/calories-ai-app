import re

DEFAULT_UNIT = "unit"

WORD_TO_NUMBER = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5
}

KNOWN_FOODS = ["rice", "roti", "dal", "salad", "chicken", "egg", "eggs", "paneer", "boiled egg"]

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

KNOWN_UNITS = ["bowl", "plate", "piece", "pieces", "cup", "cups"]

# separators for multiple foods
SEPARATORS = r",|and|with|plus"

def extract_food_items(text):
    """
    Extracts food items, quantities, and units from input text.
    Returns a list of dicts compatible with the calorie calculator.
    """
    text = text.lower()
    results = []

    # Split text by separators (and, with, plus, comma)
    parts = re.split(SEPARATORS, text)

    for part in parts:
        part = part.strip()
        for food in KNOWN_FOODS:
            if food in part:
                # Extract numeric quantity if present
                qty_match = re.search(r"(\d+)", part)
                quantity = int(qty_match.group(1)) if qty_match else 1

                # Detect unit if mentioned
                unit = DEFAULT_UNIT
                for u in KNOWN_UNITS:
                    if f"{u} of {food}" in part or f"{food} {u}" in part:
                        unit = u
                        break

                # Map to nutrition database key
                key = FOOD_ALIASES.get(food)
                if key:
                    results.append({
                        "food": key,
                        "quantity": quantity,
                        "unit": unit,
                        "confidence": 80
                    })

    return results
