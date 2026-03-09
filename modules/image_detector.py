import anthropic
import base64
import json
from pathlib import Path

client = anthropic.Anthropic()

MEDIA_TYPE_MAP = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}


def predict_food(image_path: str) -> list:
    """
    Analyzes a food image using Claude Vision.
    Returns a list of detected food items with quantities and confidence.
    Replaces the 7-class local model with unlimited food recognition.
    """
    path = Path(image_path)
    image_bytes = path.read_bytes()
    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    media_type = MEDIA_TYPE_MAP.get(path.suffix.lower(), "image/jpeg")

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=600,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": b64,
                    }
                },
                {
                    "type": "text",
                    "text": (
                        "Identify every food item visible in this image. "
                        "For each item estimate the portion size in grams. "
                        "Use lowercase underscored names (e.g. chicken_grilled, egg_boiled, white_rice). "
                        "Respond ONLY with valid JSON, no markdown, no extra text:\n"
                        '[{"food": "rice", "quantity": 1, "unit": "bowl", "grams": 150, "confidence": 90, "low_confidence": false}]'
                    )
                }
            ]
        }]
    )

    raw = response.content[0].text.strip().strip("```json").strip("```").strip()

    try:
        items = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: return empty list rather than crash
        return []

    # Ensure all required fields exist
    for item in items:
        item.setdefault("quantity", 1)
        item.setdefault("unit", "unit")
        item.setdefault("grams", 100)
        item.setdefault("confidence", 80)
        item["low_confidence"] = item.get("confidence", 80) < 60

    return items