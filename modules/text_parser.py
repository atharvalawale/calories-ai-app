import anthropic
import json

client = anthropic.Anthropic()


def extract_food_items(text: str) -> list:
    """
    Extracts food items, quantities, and units from any natural language text.
    Uses Claude API — works for any food, any language, any phrasing.
    Replaces the 9-food hardcoded keyword matcher.
    """
    if not text or not text.strip():
        return []

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": (
                f"Extract all food items from this text: '{text}'\n"
                "For each food item:\n"
                "- Use lowercase underscored names (e.g. chicken_grilled, egg_boiled, white_rice, dal)\n"
                "- Estimate quantity (number) and unit (piece/bowl/cup/grams/plate)\n"
                "- Estimate grams as best you can\n"
                "- Set confidence 0-100\n"
                "Respond ONLY with valid JSON, no markdown, no extra text:\n"
                '[{"food": "egg_boiled", "quantity": 2, "unit": "piece", "grams": 110, "confidence": 95}]'
            )
        }]
    )

    raw = response.content[0].text.strip().strip("```json").strip("```").strip()

    try:
        items = json.loads(raw)
    except json.JSONDecodeError:
        return []

    # Ensure all required fields exist
    for item in items:
        item.setdefault("quantity", 1)
        item.setdefault("unit", "unit")
        item.setdefault("grams", 100)
        item.setdefault("confidence", 80)

    return items