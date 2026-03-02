from modules.confidence import calculate_confidence

tests = [
    ("roti", 120, "unit", True),
    ("dal", 150, "bowl", True),
    ("egg", 100, "unit", False),
    ("pizza", 200, "slice", True),
    ("salad", 100, "plate", True)
]

for food, grams, unit, db_loaded in tests:
    score = calculate_confidence(food, grams, unit, db_loaded)
    print(f"{food} ({grams}g, {unit}) → Confidence: {score}%")
