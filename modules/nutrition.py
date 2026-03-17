import csv
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DEFAULT_CSV = BASE_DIR / "data" / "nutrition.csv"

NUTRITION_DB = {}

FOOD_ALIAS_MAP = {
    "egg": "egg_boiled",
    "eggs": "egg_boiled",
    "boiled egg": "egg_boiled",
    "chicken": "chicken_grilled",
}


def normalize_food_name(food_name: str) -> str:
    return food_name.strip().lower()


def load_nutrition_data(csv_path=DEFAULT_CSV) -> dict:
    """
    Loads nutrition data from CSV into memory.
    Call once at app startup.
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
                "sugar": float(row.get("sugar", 0) or 0),
                "sodium": float(row.get("sodium", 0) or 0),
            }

    return NUTRITION_DB


def get_food_nutrition(food_name: str) -> dict | None:
    """
    Returns nutrition data for a food name.
    Applies alias mapping for common name variants.
    Returns None if not found — caller must handle this.
    """
    if not NUTRITION_DB:
        raise RuntimeError("Nutrition DB not loaded. Call load_nutrition_data() first.")

    food_name = normalize_food_name(food_name)
    db_key = FOOD_ALIAS_MAP.get(food_name, food_name)

    return NUTRITION_DB.get(db_key)  