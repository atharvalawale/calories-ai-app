def apply_personalization(meal, goal=None, allergies=None):
    warnings = []
    modifier = 0

    if goal == "weight_loss" and meal["total_calories"] > 700:
        warnings.append("High calorie meal for weight loss")
        modifier -= 15

    if meal["total_sodium"] > 800:
        warnings.append("High sodium meal")

    if allergies:
        for item in meal["items"]:
            for allergen in allergies:
                if allergen.lower() in item["food"]:
                    warnings.append(f"Contains allergen: {allergen}")
                    modifier -= 30

    return warnings, modifier