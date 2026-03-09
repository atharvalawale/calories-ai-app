import requests


def fetch_product(barcode: str) -> dict:
    """
    Fetches product nutrition from OpenFoodFacts by barcode.
    Returns a nutrition dict or {"error": "..."} on failure.
    """
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        return {"error": "Request timed out"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

    data = response.json()

    if data.get("status") != 1:
        return {"error": "Product not found"}

    product = data["product"]
    nutriments = product.get("nutriments", {})

    return {
        "name": product.get("product_name", "Unknown"),
        "brand": product.get("brands", ""),
        "serving_size": product.get("serving_size", "100g"),
        "calories_per_100g": nutriments.get("energy-kcal_100g", 0),
        "protein_g": nutriments.get("proteins_100g", 0),
        "carbs_g": nutriments.get("carbohydrates_100g", 0),
        "fat_g": nutriments.get("fat_100g", 0),
        "sugar_g": nutriments.get("sugars_100g", 0),
        "sodium_mg": nutriments.get("sodium_100g", 0) * 1000,   # converted g → mg
        "fiber_g": nutriments.get("fiber_100g", 0),
        "ingredients": product.get("ingredients_text", ""),
        "allergens": product.get("allergens_tags", []),
        "nutriscore": product.get("nutriscore_grade", "?").upper(),
        "labels": product.get("labels_tags", []),
    }