def compute_meal_health_score(meal):
    score = 100

    score -= meal["total_sugar"] * 1.5
    score -= meal["total_sodium"] * 0.02
    score -= meal["total_fat"] * 0.8

    score = max(round(score, 2), 0)

    if score >= 80:
        category = "Excellent"
    elif score >= 60:
        category = "Good"
    elif score >= 40:
        category = "Moderate"
    else:
        category = "Poor"

    return score, category