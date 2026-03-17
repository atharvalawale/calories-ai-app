GOAL_CALORIE_LIMITS = {
    "weight_loss": 600,
    "maintenance": 800,
    "muscle_gain": 1000,
}

GOAL_PROTEIN_TARGETS = {
    "muscle_gain": 30,  # minimum grams of protein per meal
}


def apply_personalization(meal, goal=None, allergies=None):
    """
    Checks a meal against user goal and allergies.
    Returns (warning_string, score_modifier).
    """
    warnings = []
    modifier = 0

    if goal and goal in GOAL_CALORIE_LIMITS:
        limit = GOAL_CALORIE_LIMITS[goal]
        if meal["total_calories"] > limit:
            warnings.append(f"High calorie meal for {goal.replace('_', ' ')} goal (>{limit} kcal)")
            modifier -= 15

    if goal == "muscle_gain":
        if meal.get("total_protein", 0) < GOAL_PROTEIN_TARGETS["muscle_gain"]:
            warnings.append("Low protein for muscle gain goal (<30g per meal)")
            modifier -= 10

    if meal.get("total_sodium", 0) > 800:
        warnings.append("High sodium meal (>800mg)")
        modifier -= 5

    if meal.get("total_sugar", 0) > 20:
        warnings.append("High sugar content (>20g)")
        modifier -= 5

    if allergies:
        for item in meal.get("items", []):
            food_text = (
                item.get("food", "") + " " +
                item.get("ingredients", "")
            ).lower()
            for allergen in allergies:
                if allergen.lower() in food_text:
                    warnings.append(f"⚠️ Allergen detected: {allergen} in {item['food']}")
                    modifier -= 30

    warning_str = " | ".join(warnings) if warnings else ""
    return warning_str, modifier
