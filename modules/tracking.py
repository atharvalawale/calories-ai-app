# modules/tracking.py

from typing import List, Dict

# ===============================
# GOAL TARGETS
# ===============================

GOAL_TARGETS = {
    "maintenance": {"calories": 2200, "protein": 100},
    "weight_loss": {"calories": 1800, "protein": 120},
    "muscle_gain": {"calories": 2800, "protein": 150},
}

# ===============================
# DAILY TOTAL CALCULATION
# ===============================

def calculate_daily_totals(log: List[Dict]) -> Dict:
    totals = {
        "calories": 0.0,
        "protein": 0.0,
        "carbs": 0.0,
        "fat": 0.0,
        "sugar": 0.0,
        "sodium": 0.0,
    }

    for meal in log:
        totals["calories"] += meal.get("total_calories", 0)
        totals["protein"] += meal.get("total_protein", 0)
        totals["carbs"] += meal.get("total_carbs", 0)
        totals["fat"] += meal.get("total_fat", 0)
        totals["sugar"] += meal.get("total_sugar", 0)
        totals["sodium"] += meal.get("total_sodium", 0)

    for key in totals:
        totals[key] = round(totals[key], 2)

    return totals


def get_goal_targets(goal: str) -> Dict:
    return GOAL_TARGETS.get(goal, GOAL_TARGETS["maintenance"])


def generate_recommendation(daily_totals: Dict, goal_targets: Dict) -> str:

    if daily_totals["calories"] > goal_targets["calories"]:
        return "You have exceeded your calorie target for today."

    if daily_totals["protein"] < goal_targets["protein"]:
        deficit = goal_targets["protein"] - daily_totals["protein"]
        return f"You are {round(deficit,1)}g short of your protein goal."

    return "You are on track with your nutrition goals."