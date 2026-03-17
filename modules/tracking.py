# ─────────────────────────────────────────────
# tracking.py — Daily nutrition tracking + AI recommendations
# ─────────────────────────────────────────────

# WHY THIS FILE EXISTS:
# After user logs meals throughout the day, we need to:
# 1. Add up all nutrition (daily totals)
# 2. Compare against their goal targets
# 3. Give smart AI-powered recommendations
# 4. Track streaks — how many days in a row they hit their goal

# ── IMPORTS ────────────────────────────────────────────────────────────────────

import google.generativeai as genai   # Gemini AI for smart recommendations
import json                            # to parse Gemini's JSON response
import os                              # to read API key from environment
from datetime import datetime, timedelta  # for date calculations and streaks

# Configure Gemini — reads key from environment variable
# WHY os.environ.get: never hardcode API keys in code!
# If you push to GitHub with hardcoded key → anyone can use your account!
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "your-gemini-key-here"))
model = genai.GenerativeModel("gemini-2.0-flash")

# ── GOAL TARGETS ───────────────────────────────────────────────────────────────
# WHY DICTIONARY OF DICTIONARIES:
# Each goal has multiple targets — calories, protein, carbs, fat.
# A dict of dicts is the cleanest way to organize this.
# Called a "nested dictionary" — dictionary inside a dictionary.

GOAL_TARGETS = {
    "weight_loss": {
        "calories": 1600,   # lower calories → burn fat
        "protein":  120,    # high protein → preserve muscle while losing fat
        "carbs":    150,    # lower carbs → less energy stored as fat
        "fat":       50,    # moderate fat
        "fiber":     25,    # high fiber → keeps you full longer
        "sugar":     25,    # low sugar → avoid insulin spikes
        "sodium":  2000,    # standard sodium limit
    },
    "muscle_gain": {
        "calories": 2800,   # more calories → fuel for muscle growth
        "protein":  180,    # very high protein → builds muscle
        "carbs":    350,    # high carbs → energy for workouts
        "fat":       80,    # higher fat → hormone production
        "fiber":     30,
        "sugar":     40,
        "sodium":  2300,
    },
    "maintenance": {
        "calories": 2000,   # standard adult daily requirement
        "protein":  100,    # standard protein
        "carbs":    250,    # standard carbs
        "fat":       65,    # standard fat
        "fiber":     25,
        "sugar":     30,
        "sodium":  2300,
    }
}


# ── FUNCTION 1: Calculate Daily Totals ─────────────────────────────────────────

def calculate_daily_totals(daily_log: list) -> dict:
    """
    Adds up all nutrition from all meals logged today.

    Input:  list of meal dicts from calorie_calculator.py
    Output: single dict with total nutrition for the day

    Example input:
    [
        {"total_calories": 450, "total_protein": 25, ...},  # breakfast
        {"total_calories": 600, "total_protein": 30, ...},  # lunch
    ]

    Example output:
    {"calories": 1050, "protein": 55, ...}
    """

    # WHY start at 0: accumulator pattern
    # we add each meal's nutrition one by one
    totals = {
        "calories": 0,
        "protein":  0,
        "carbs":    0,
        "fat":      0,
        "fiber":    0,
        "sugar":    0,
        "sodium":   0,
    }

    # WHY loop through daily_log:
    # user might have logged 1 meal or 10 meals
    # we don't know how many — loop handles any number
    for meal in daily_log:

        # WHY .get() with 0:
        # some meals might not have all fields
        # barcode products might be missing fiber for example
        # .get() safely returns 0 instead of crashing
        totals["calories"] += meal.get("total_calories", 0)
        totals["protein"]  += meal.get("total_protein",  0)
        totals["carbs"]    += meal.get("total_carbs",    0)
        totals["fat"]      += meal.get("total_fat",      0)
        totals["fiber"]    += meal.get("total_fiber",    0)
        totals["sugar"]    += meal.get("total_sugar",    0)
        totals["sodium"]   += meal.get("total_sodium",   0)

    # WHY round: 450.333333 is ugly. 450.3 is clean.
    # round each value to 1 decimal place
    return {k: round(v, 1) for k, v in totals.items()}
    # NOTE: this is called "dictionary comprehension"
    # {k: round(v, 1) for k, v in totals.items()}
    # means: for every key-value pair, round the value


# ── FUNCTION 2: Get Goal Targets ───────────────────────────────────────────────

def get_goal_targets(goal: str) -> dict:
    """
    Returns daily nutrition targets for a given goal.

    Input:  goal string — "weight_loss", "muscle_gain", "maintenance"
    Output: dict of targets

    WHY this function exists:
    app.py needs targets to show progress bars.
    Instead of app.py accessing GOAL_TARGETS directly,
    it calls this function. This way if we change GOAL_TARGETS,
    app.py doesn't need to change.
    This is called "abstraction" — hiding internal details.
    """

    # WHY .get() with maintenance default:
    # if unknown goal passed → return maintenance targets
    # safer than crashing with KeyError
    return GOAL_TARGETS.get(goal, GOAL_TARGETS["maintenance"])


# ── FUNCTION 3: Calculate Progress ─────────────────────────────────────────────

def calculate_progress(daily_totals: dict, goal: str) -> dict:
    """
    Compares daily totals against targets and calculates progress %.

    Input:  daily totals dict + goal string
    Output: dict showing progress for each nutrient

    WHY this function:
    app.py needs to show progress bars.
    "You ate 1200 out of 1600 calories = 75%"
    This function calculates all those percentages.
    """

    targets = get_goal_targets(goal)
    progress = {}

    for nutrient, target in targets.items():

        actual = daily_totals.get(nutrient, 0)

        # WHY check target > 0:
        # prevent division by zero crash
        # if target is somehow 0, percentage would be infinity
        if target > 0:
            percentage = round((actual / target) * 100, 1)
        else:
            percentage = 0

        # WHY min(..., 100):
        # if user ate MORE than target, percentage would be >100
        # progress bar can't show >100% — cap it at 100
        progress[nutrient] = {
            "actual":     actual,
            "target":     target,
            "percentage": min(percentage, 100),
            "remaining":  max(round(target - actual, 1), 0),
            "exceeded":   actual > target
        }

    return progress


# ── FUNCTION 4: AI Recommendation (Gemini) ─────────────────────────────────────

def generate_recommendation(daily_totals: dict, goal: str) -> str:
    """
    Uses Gemini AI to generate personalized nutrition recommendations.

    Input:  daily totals + goal
    Output: personalized recommendation string

    WHY Gemini instead of hardcoded rules:
    Hardcoded rules can only handle what we anticipated.
    Gemini understands context and gives nuanced advice.

    Example hardcoded rule:
    if calories < target: return "Eat more"  ← boring and generic

    Example Gemini response:
    "You've hit your protein goal but you're 400 calories short.
     Consider a high-protein snack like Greek yogurt or boiled eggs
     before bed to meet your muscle gain targets." ← specific and useful
    """

    targets = get_goal_targets(goal)
    progress = calculate_progress(daily_totals, goal)

    # WHY build a detailed prompt:
    # The more context we give Gemini, the better its advice
    # We tell it: goal, what user ate, what targets are, what's remaining
    prompt = f"""
    You are a professional nutritionist AI assistant.
    
    User's goal: {goal.replace('_', ' ')}
    
    Today's nutrition so far:
    - Calories:  {daily_totals.get('calories', 0)} / {targets['calories']} kcal
    - Protein:   {daily_totals.get('protein',  0)}g / {targets['protein']}g
    - Carbs:     {daily_totals.get('carbs',    0)}g / {targets['carbs']}g
    - Fat:       {daily_totals.get('fat',      0)}g / {targets['fat']}g
    - Fiber:     {daily_totals.get('fiber',    0)}g / {targets['fiber']}g
    - Sugar:     {daily_totals.get('sugar',    0)}g / {targets['sugar']}g
    - Sodium:    {daily_totals.get('sodium',   0)}mg / {targets['sodium']}mg
    
    Give a SHORT and SPECIFIC recommendation (2-3 sentences max).
    Focus on what the user should eat NEXT to meet their goals.
    Be encouraging and practical.
    Suggest specific Indian foods where possible.
    Do NOT repeat the numbers back — just give actionable advice.
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        # WHY fallback:
        # if Gemini API fails (no internet, rate limit etc.)
        # we don't want app to crash — return a basic message instead
        return generate_basic_recommendation(daily_totals, targets)


# ── FUNCTION 5: Basic Recommendation (Fallback) ────────────────────────────────

def generate_basic_recommendation(daily_totals: dict, targets: dict) -> str:
    """
    Simple rule-based recommendation — used as fallback if Gemini fails.

    WHY this exists:
    Defensive programming — always have a backup plan.
    If Gemini API is down, app still gives SOME recommendation.
    Not as good as Gemini but better than crashing or showing nothing.
    """

    calories_remaining = targets["calories"] - daily_totals.get("calories", 0)
    protein_remaining  = targets["protein"]  - daily_totals.get("protein",  0)

    # WHY check calories first:
    # calories is the most important macro for any goal
    if calories_remaining > 500:
        return f"You still have {round(calories_remaining)} calories remaining today. Consider a balanced meal with protein and vegetables."
    elif calories_remaining > 200:
        return f"You're close to your calorie goal! Just {round(calories_remaining)} calories remaining. A light snack would be perfect."
    elif calories_remaining < 0:
        return f"You've exceeded your calorie target by {round(abs(calories_remaining))} calories. Focus on light, protein-rich foods for the rest of the day."
    elif protein_remaining > 20:
        return f"You've hit your calorie goal but still need {round(protein_remaining)}g more protein. Try eggs, dal, or paneer."
    else:
        return "Great job! You're on track with your nutrition goals today. Keep it up!"


# ── FUNCTION 6: Streak Tracker ─────────────────────────────────────────────────

def calculate_streak(streak_log: list) -> dict:
    """
    Calculates how many days in a row user hit their calorie goal.

    Input:  list of booleans — True if goal hit, False if not
            e.g. [True, True, False, True, True, True]
    Output: dict with current streak and longest streak

    WHY streaks:
    Research shows streaks increase motivation and habit formation.
    Same psychology used by Duolingo, fitness apps, etc.
    Users are more likely to stay consistent if they can see a streak.
    """

    if not streak_log:
        return {"current_streak": 0, "longest_streak": 0}

    # WHY calculate from the end:
    # current streak = consecutive True values from TODAY backwards
    current_streak = 0
    for day in reversed(streak_log):
        if day:
            current_streak += 1
        else:
            break   # streak broken — stop counting

    # WHY calculate longest separately:
    # user might have had a longer streak in the past
    # we want to show their best ever streak too
    longest_streak = 0
    current_count  = 0

    for day in streak_log:
        if day:
            current_count += 1
            longest_streak = max(longest_streak, current_count)
        else:
            current_count = 0   # reset on broken day

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "streak_emoji":   "🔥" * min(current_streak, 5)  # max 5 fire emojis
    }


# ── FUNCTION 7: Weekly Summary ─────────────────────────────────────────────────

def calculate_weekly_summary(weekly_logs: list, goal: str) -> dict:
    """
    Calculates average daily nutrition over the past 7 days.

    Input:  list of 7 daily_total dicts (one per day)
    Output: averages + how many days goal was hit

    WHY weekly summary:
    Daily view can be misleading — one bad day doesn't mean failure.
    Weekly average gives a more accurate picture of eating habits.
    """

    if not weekly_logs:
        return {}

    targets = get_goal_targets(goal)

    # WHY sum then divide:
    # to get average, add all values then divide by count
    # same as school average calculation
    totals = {
        "calories": 0, "protein": 0,
        "carbs": 0,    "fat": 0,
    }

    days_goal_hit = 0

    for day in weekly_logs:
        for nutrient in totals:
            totals[nutrient] += day.get(nutrient, 0)

        # WHY check within 10%:
        # hitting exactly 2000 calories every day is unrealistic
        # within 10% of target = success
        # e.g. target 2000 → anywhere between 1800-2200 = hit ✅
        calorie_target  = targets["calories"]
        calorie_actual  = day.get("calories", 0)
        tolerance       = calorie_target * 0.10   # 10% tolerance

        if abs(calorie_actual - calorie_target) <= tolerance:
            days_goal_hit += 1

    # Calculate averages
    days = len(weekly_logs)
    averages = {k: round(v / days, 1) for k, v in totals.items()}

    return {
        "averages":       averages,
        "days_goal_hit":  days_goal_hit,
        "days_total":     days,
        "consistency":    f"{round((days_goal_hit / days) * 100)}%"
    }