import google.generativeai as genai
import json
import os

genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "your-gemini-key-here"))
model = genai.GenerativeModel("gemini-2.0-flash")


def extract_food_items(text: str) -> list:
    """
    Extracts food items, quantities, and units from any natural language text.
    Uses Gemini API (free tier: 1500 req/day) — works for any food, any language, any phrasing.
    """
    if not text or not text.strip():
        return []

    prompt = (
        f"Extract all food items from this text: '{text}'\n"
        "For each food item:\n"
        "- Use lowercase underscored names (e.g. chicken_grilled, egg_boiled, white_rice, dal)\n"
        "- Estimate quantity (number) and unit (piece/bowl/cup/grams/plate)\n"
        "- Estimate grams as best you can\n"
        "- Set confidence 0-100\n"
        "Respond ONLY with valid JSON, no markdown, no extra text:\n"
        '[{"food": "egg_boiled", "quantity": 2, "unit": "piece", "grams": 110, "confidence": 95}]'
    )

    response = model.generate_content(prompt)
    raw = response.text.strip().strip("```json").strip("```").strip()

    try:
        items = json.loads(raw)
    except json.JSONDecodeError:
        return []

    for item in items:
        item.setdefault("quantity", 1)
        item.setdefault("unit", "unit")
        item.setdefault("grams", 100)
        item.setdefault("confidence", 80)

    return items