from modules.nutrition import get_food_nutrition

def calculate_calories(food, grams):
    nutrition = get_food_nutrition(food)

    if nutrition is None:
        return None

    factor = grams / 100

    return {
        "food": food,
        "grams": grams,
        "calories": nutrition["calories_100g"] * factor,
        "protein": nutrition["protein"] * factor,
        "carbs": nutrition["carbs"] * factor,
        "fat": nutrition["fat"] * factor
    }

def calculate_meal_totals(portions):
    meal_items = []
    total_cal = total_pro = total_carb = total_fat = 0

    for item in portions:
        food = item["food"]
        grams = item["grams"]

        result = calculate_calories(food, grams)

        if result:
            meal_items.append(result)
            total_cal += result["calories"]
            total_pro += result["protein"]
            total_carb += result["carbs"]
            total_fat += result["fat"]

    return {
        "items": meal_items,
        "total_calories": round(total_cal, 2),
        "total_protein": round(total_pro, 2),
        "total_carbs": round(total_carb, 2),
        "total_fat": round(total_fat, 2)
    }
