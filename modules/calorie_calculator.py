from modules.nutrition import get_food_nutrition

def calculate_calories(food, grams):
    nutrition = get_food_nutrition(food)
<<<<<<< HEAD
=======

>>>>>>> 0b17e81dcefa826614e4d2c4e1e0748f61fcb827
    if nutrition is None:
        return None

    factor = grams / 100

    return {
        "food": food,
        "grams": grams,
        "calories": nutrition["calories_100g"] * factor,
        "protein": nutrition["protein"] * factor,
        "carbs": nutrition["carbs"] * factor,
<<<<<<< HEAD
        "fat": nutrition["fat"] * factor,
        "sugar": nutrition.get("sugar", 0) * factor,
        "sodium": nutrition.get("sodium", 0) * factor
=======
        "fat": nutrition["fat"] * factor
>>>>>>> 0b17e81dcefa826614e4d2c4e1e0748f61fcb827
    }

def calculate_meal_totals(portions):
    meal_items = []
<<<<<<< HEAD
    totals = {
        "calories": 0,
        "protein": 0,
        "carbs": 0,
        "fat": 0,
        "sugar": 0,
        "sodium": 0
    }

    for item in portions:
        result = calculate_calories(item["food"], item["grams"])
        if result:
            meal_items.append(result)
            for key in totals:
                totals[key] += result[key]

    return {
        "items": meal_items,
        "total_calories": round(totals["calories"], 2),
        "total_protein": round(totals["protein"], 2),
        "total_carbs": round(totals["carbs"], 2),
        "total_fat": round(totals["fat"], 2),
        "total_sugar": round(totals["sugar"], 2),
        "total_sodium": round(totals["sodium"], 2),
    }
=======
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
>>>>>>> 0b17e81dcefa826614e4d2c4e1e0748f61fcb827
