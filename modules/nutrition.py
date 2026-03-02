import csv
from pathlib import Path

<<<<<<< HEAD
NUTRITION_DB = {}

def normalize_food_name(food_name: str):
    return food_name.strip().lower()

def load_nutrition_data(csv_path="data/nutrition.csv"):
=======
# Global dictionary to store nutrition data
NUTRITION_DB = {}

def load_nutrition_data(csv_path="data/nutrition.csv"):
    """
    Loads nutrition data from CSV into a dictionary.
    Call this once at app startup.
    """
>>>>>>> 0b17e81dcefa826614e4d2c4e1e0748f61fcb827
    global NUTRITION_DB
    NUTRITION_DB = {}

    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(f"Nutrition file not found: {csv_path}")

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
<<<<<<< HEAD
            food = normalize_food_name(row["food"])
=======
            food = row["food"].strip().lower()
>>>>>>> 0b17e81dcefa826614e4d2c4e1e0748f61fcb827
            NUTRITION_DB[food] = {
                "calories_100g": float(row["calories_100g"]),
                "protein": float(row["protein"]),
                "carbs": float(row["carbs"]),
                "fat": float(row["fat"]),
<<<<<<< HEAD
                "sugar": float(row.get("sugar", 0)),
                "sodium": float(row.get("sodium", 0)),
=======
>>>>>>> 0b17e81dcefa826614e4d2c4e1e0748f61fcb827
            }

    return NUTRITION_DB

<<<<<<< HEAD
def get_food_nutrition(food_name):
    if not NUTRITION_DB:
        raise RuntimeError("Nutrition database not loaded.")

    food_name = normalize_food_name(food_name)
    return NUTRITION_DB.get(food_name)
=======

def get_food_nutrition(food_name):
    """
    Returns nutrition data for a given food.
    Maps detected food names to CSV entries if necessary.
    """
    if not NUTRITION_DB:
        raise RuntimeError("Nutrition database not loaded. Call load_nutrition_data() first.")

    food_name = food_name.strip().lower()

    # Minimal mapping for foods that don't match CSV exactly
    food_map = {
        "egg": "egg_boiled",
        "chicken": "chicken_grilled"
        # Add more mappings if needed
    }

    db_food_name = food_map.get(food_name, food_name)

    return NUTRITION_DB.get(db_food_name)
>>>>>>> 0b17e81dcefa826614e4d2c4e1e0748f61fcb827
