import csv
from pathlib import Path

# Global dictionary to store nutrition data
NUTRITION_DB = {}


def normalize_food_name(food_name: str):
    return food_name.strip().lower()


def load_nutrition_data(csv_path="data/nutrition.csv"):
    """
    Loads nutrition data from CSV into memory.
    Call this once at app startup.
    """
    global NUTRITION_DB
    NUTRITION_DB = {}

    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(f"Nutrition file not found: {csv_path}")

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            food = normalize_food_name(row["food"])

            NUTRITION_DB[food] = {
                "calories_100g": float(row["calories_100g"]),
                "protein": float(row["protein"]),
                "carbs": float(row["carbs"]),
                "fat": float(row["fat"]),
                "sugar": float(row.get("sugar", 0)),
                "sodium": float(row.get("sodium", 0)),
            }

    return NUTRITION_DB


def get_food_nutrition(food_name):
    """
    Returns nutrition data for a given food.
    Applies minimal mapping if needed.
    """
    if not NUTRITION_DB:
        raise RuntimeError("Nutrition database not loaded. Call load_nutrition_data() first.")

    food_name = normalize_food_name(food_name)

    # Optional mapping for mismatched detector names
    food_map = {
        "egg": "egg_boiled",
        "chicken": "chicken_grilled",
    }

    db_food_name = food_map.get(food_name, food_name)

    return NUTRITION_DB.get(db_food_name)