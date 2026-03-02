import requests

def fetch_product(barcode: str):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()

    if data.get("status") != 1:
        return None

    product = data["product"]
    nutriments = product.get("nutriments", {})

    return {
        "name": product.get("product_name", "Unknown"),
        "calories": nutriments.get("energy-kcal_100g", 0),
        "protein": nutriments.get("proteins_100g", 0),
        "carbs": nutriments.get("carbohydrates_100g", 0),
        "fat": nutriments.get("fat_100g", 0),
        "sugar": nutriments.get("sugars_100g", 0),
        "sodium": nutriments.get("sodium_100g", 0),
        "ingredients": product.get("ingredients_text", "")
    }