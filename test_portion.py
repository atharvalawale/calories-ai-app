from modules.portion import estimate_portion

tests = [
    ("roti", 2, "unit"),
    ("dal", 1, "bowl"),
    ("rice", 1, "bowl"),
    ("egg", 2, "unit"),
    ("paneer", 1, "unit"),
    ("salad", 1, "plate")
]

for food, qty, unit in tests:
    grams, note = estimate_portion(food, qty, unit)
    print(food, "→", grams, "g")
    print("  ", note)
