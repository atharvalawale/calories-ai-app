import re

# Default units if user does not specify
DEFAULT_UNIT = "unit"

# Common quantity words mapped to numbers
WORD_TO_NUMBER = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4
}

# Known food keywords (expand later)
KNOWN_FOODS = [
    "rice",
    "roti",
    "dal",
    "salad",
    "chicken",
    "egg",
    "paneer"
]

# Common units
KNOWN_UNITS = ["bowl", "plate", "piece", "pieces", "cup", "cups"]


def extract_food_items(text):
    """
    Extracts food items, quantity, and unit from input text.
    Returns a list of dictionaries.
    """
    text = text.lower()

    results = []

    for food in KNOWN_FOODS:
        if food in text:
            quantity = 1
            unit = DEFAULT_UNIT

            # Check numeric quantity (e.g., "2 rotis")
            qty_match = re.search(r"(\d+)\s+" + food, text)
            if qty_match:
                quantity = int(qty_match.group(1))
            else:
                # Check word-based quantity (e.g., "two rotis")
                for word, number in WORD_TO_NUMBER.items():
                    if f"{word} {food}" in text:
                        quantity = number

            # Check unit
            for u in KNOWN_UNITS:
                if f"{u} of {food}" in text or f"{food} {u}" in text:
                    unit = u

            results.append({
                "food": food,
                "quantity": quantity,
                "unit": unit
            })

    return results
