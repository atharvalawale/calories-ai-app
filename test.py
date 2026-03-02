from modules.nutrition import load_nutrition_data, get_food_nutrition

# Load nutrition data
load_nutrition_data()

# Test known foods
print("Rice:", get_food_nutrition("rice"))
print("Dal:", get_food_nutrition("dal"))

# Test unknown food
print("Pizza:", get_food_nutrition("pizza"))
