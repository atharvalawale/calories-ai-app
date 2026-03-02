from modules.nutrition import load_nutrition_data
from modules.calorie_calculator import calculate_meal_totals

# 1️⃣ Load nutrition database
load_nutrition_data()

# 2️⃣ Sample food with grams from Task 3
meal = [
    {"food": "roti", "grams": 120},
    {"food": "dal", "grams": 150},
    {"food": "rice", "grams": 150},
    {"food": "egg", "grams": 100},
    {"food": "paneer", "grams": 100},
    {"food": "salad", "grams": 100}
]

# 3️⃣ Calculate meal totals
result = calculate_meal_totals(meal)

# Print per-item details
for item in result["meal_details"]:
    print(item)

# Print totals
print("\nMeal Totals:", result["totals"])
