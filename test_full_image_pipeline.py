import json
from modules.image_detector import predict_food
from modules.portion import estimate_portion
from modules.calorie_calculator import calculate_meal_totals
from modules.confidence import compute_confidence
from modules.nutrition import load_nutrition_data

# load nutrition DB
load_nutrition_data()

image_path = r"C:\Calorie AI app\dataset\test\salad\salad6.jpg"

# STEP 1: detect food
foods = predict_food(image_path)

# STEP 2: portion
portions = estimate_portion(foods)

# STEP 3: calories
meal = calculate_meal_totals(portions)

# STEP 4: confidence
conf = compute_confidence(foods)

# FINAL OUTPUT
output = {
    "detected_food": foods,
    "portions": portions,
    "meal": meal,
    "confidence": conf
}

print(json.dumps(output, indent=4))

# Save file
with open("output.json", "w") as f:
    json.dump(output, f, indent=4)
