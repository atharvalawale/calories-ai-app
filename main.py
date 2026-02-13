from modules.image_detector import predict_food
from modules.portion import estimate_portion
from modules.calorie_calculator import calculate_meal_totals
from modules.confidence import compute_confidence
from modules.nutrition import load_nutrition_data
import json

# load nutrition DB
load_nutrition_data()

# input image
image_path = input("Enter image path: ")

# STEP 1: detect
foods = predict_food(image_path)

# STEP 2: portion
portions = estimate_portion(foods)

# STEP 3: calories
meal = calculate_meal_totals(portions)

# STEP 4: confidence
conf = compute_confidence(foods)

# PRINT OUTPUT
print("\n===== RESULT =====")
print("Detected:", foods)
print("Portions:", portions)
print("Meal:", meal)
print("Confidence:", conf)

# SAVE JSON (important for task)
output = {
    "detected_food": foods,
    "portions": portions,
    "meal": meal,
    "confidence": conf
}

with open("output.json", "w") as f:
    json.dump(output, f, indent=4)

print("\nSaved → output.json")
