
SUGAR_PENALTY    = 1.5    # per gram  — high penalty, sugar is very harmful
SODIUM_PENALTY   = 0.02   # per mg    — small number because sodium is in mg not g
FAT_PENALTY      = 0.5    # per gram  — medium penalty, some fat is necessary
CALORIE_PENALTY  = 0.03   # per kcal  — small penalty for high calorie meals



PROTEIN_REWARD   = 0.8    # per gram  — high reward, protein is very beneficial
FIBER_REWARD     = 1.2    # per gram  — highest reward, fiber is extremely healthy



SCORE_EXCELLENT  = 80
SCORE_GOOD       = 60
SCORE_MODERATE   = 40
BASE_SCORE       = 100    # everyone starts with perfect score


def compute_meal_health_score(meal: dict) -> tuple:
    """
    Calculates a health score (0-100) for a meal.

    Input:  meal dict from calorie_calculator.py
    Output: (score, category) e.g. (72.5, "Good")

    Scoring logic:
    - Start at 100
    - Subtract points for sugar, sodium, fat, calories
    - Add points for protein and fiber
    - Cap between 0 and 100
    """

    score = BASE_SCORE


    sugar_loss   = meal.get("total_sugar",    0) * SUGAR_PENALTY
    sodium_loss  = meal.get("total_sodium",   0) * SODIUM_PENALTY
    fat_loss     = meal.get("total_fat",      0) * FAT_PENALTY
    calorie_loss = meal.get("total_calories", 0) * CALORIE_PENALTY

    score -= sugar_loss
    score -= sodium_loss
    score -= fat_loss
    score -= calorie_loss

 
    protein_gain = meal.get("total_protein", 0) * PROTEIN_REWARD

   
    fiber_gain   = meal.get("total_fiber",   0) * FIBER_REWARD

    score += protein_gain
    score += fiber_gain


    score = min(max(round(score, 1), 0), 100)


    if score >= SCORE_EXCELLENT:
        category = "Excellent 🟢"
    elif score >= SCORE_GOOD:
        category = "Good 🟡"
    elif score >= SCORE_MODERATE:
        category = "Moderate 🟠"
    else:
        category = "Poor 🔴"

 
    breakdown = {
        "penalties": {
            "sugar":    round(sugar_loss,   1),
            "sodium":   round(sodium_loss,  1),
            "fat":      round(fat_loss,     1),
            "calories": round(calorie_loss, 1),
        },
        "rewards": {
            "protein": round(protein_gain, 1),
            "fiber":   round(fiber_gain,   1),
        }
    }


    return score, category, breakdown