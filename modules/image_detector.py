import google.generativeai as genai
import base64
import json
from pathlib import Path
import os

genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "your-gemini-key-here"))
model = genai.GenerativeModel("gemini-2.0-flash")

MEDIA_TYPE_MAP = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}


def predict_food(image_path: str) -> list:
    """
    Analyzes a food image using Gemini Vision (free tier: 1500 req/day).
    Returns a list of detected food items with quantities and confidence.
    """
    path = Path(image_path)
    image_bytes = path.read_bytes()
    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    media_type = MEDIA_TYPE_MAP.get(path.suffix.lower(), "image/jpeg")

    prompt = (
        "Identify every food item visible in this image. "
        "For each item estimate the portion size in grams. "
        "Use lowercase underscored names (e.g. chicken_grilled, egg_boiled, white_rice). "
        "Respond ONLY with valid JSON, no markdown, no extra text:\n"
        '[{"food": "rice", "quantity": 1, "unit": "bowl", "grams": 150, "confidence": 90, "low_confidence": false}]'
    )

    response = model.generate_content([
        {"mime_type": media_type, "data": b64},
        prompt
    ])

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
        item["low_confidence"] = item.get("confidence", 80) < 60

    return items