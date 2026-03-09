from modules.nutrition import get_food_nutrition


def calculate_calories(food: str, grams: float) -> dict | None:
    """
    Calculates nutrition for a single food item given weight in grams.
    Returns None if food not found or grams is invalid.
    """
    if not grams or grams <= 0:
        return None

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
        "fat": nutrition["fat"] * factor,
        "sugar": nutrition.get("sugar", 0) * factor,
        "sodium": nutrition.get("sodium", 0) * factor,
    }


def calculate_meal_totals(portions: list) -> dict:
    """
    Calculates total nutrition for a list of food portions.
    Skipped foods (not in DB) are tracked and returned separately.
    """
    meal_items = []
    skipped = []

    totals = {
        "calories": 0,
        "protein": 0,
        "carbs": 0,
        "fat": 0,
        "sugar": 0,
        "sodium": 0,
    }

    for item in portions:
        result = calculate_calories(item["food"], item.get("grams", 100))

        if result:
            meal_items.append(result)
            for key in totals:
                totals[key] += result[key]
        else:
            skipped.append(item["food"])

    return {
        "items": meal_items,
        "total_calories": round(totals["calories"], 2),
        "total_protein": round(totals["protein"], 2),
        "total_carbs": round(totals["carbs"], 2),
        "total_fat": round(totals["fat"], 2),
        "total_sugar": round(totals["sugar"], 2),
        "total_sodium": round(totals["sodium"], 2),
        "skipped_foods": skipped,   # caller can warn user about unrecognized foods
    }