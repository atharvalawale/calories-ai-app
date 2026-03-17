# ─────────────────────────────────────────────
# portion.py — Converts detected foods into grams
# ─────────────────────────────────────────────



PORTION_DB = {
    "rice":              200,   # 1 standard bowl cooked rice
    "white_rice":        200,
    "brown_rice":        185,
    "fried_rice":        200,
    "biryani":           250,
    "roti":               50,   # 1 roti/chapati
    "chapati":            50,
    "naan":               90,
    "paratha":           100,
    "bread":              60,   # 2 slices
    "toast":              60,
    "pasta":             220,   # 1 bowl cooked
    "noodles":           200,
    "pizza":             150,   # 1 medium slice
    "burger":            200,
    "sandwich":          180,
    "idli":               80,   # 2 idlis
    "dosa":              100,
    "upma":              180,
    "poha":              150,

    "dal":               180,   # 1 katori/bowl
    "dal_tadka":         180,
    "dal_makhani":       200,
    "rajma":             180,
    "chhole":            180,
    "sambar":            180,
    "lentil_soup":       200,

    "egg_boiled":         60,   # 1 large egg
    "egg":                60,
    "eggs":               60,
    "egg_fried":          70,
    "egg_scrambled":      90,   # cooked with butter
    "chicken_grilled":   200,
    "chicken":           200,
    "chicken_curry":     250,
    "chicken_tikka":     150,
    "mutton":            200,
    "fish":              150,
    "fish_curry":        200,
    "paneer":            120,   # 1 standard serving
    "paneer_curry":      200,
    "tofu":              120,

    "salad":             100,
    "vegetable_curry":   150,
    "sabzi":             150,
    "mixed_vegetables":  150,
    "palak":             150,   # spinach dish
    "aloo":              150,   # potato dish

    "milk":              240,   # 1 glass
    "curd":              150,   # 1 katori
    "yogurt":            150,
    "raita":             120,
    "paneer_raw":        100,
    "cheese":             30,   # 1 slice

    "samosa":             80,   # 1 samosa
    "pakora":             80,
    "chips":              30,   # 1 small packet
    "biscuit":            20,   # 1 biscuit

    "banana":            120,   # 1 medium
    "apple":             150,   # 1 medium
    "mango":             200,   # 1 cup sliced
    "orange":            130,

    "chai":              150,   # 1 cup with milk & sugar
    "tea":               150,
    "coffee":            150,
    "juice":             240,   # 1 glass
    "lassi":             250,
}



UNIT_MULTIPLIERS = {
    "teaspoon":  0.10,
    "tsp":       0.10,
    "tablespoon":0.20,
    "tbsp":      0.20,
    "slice":     0.60,
    "piece":     1.00,
    "cup":       0.75,

   
    "unit":      1.00,   # default — no adjustment
    "serving":   1.00,
    "bowl":      1.00,
    "katori":    1.00,   # Indian standard bowl
    "glass":     1.00,

   
    "plate":     1.50,
    "large":     1.50,
    "full":      2.00,
}


DEFAULT_GRAMS = 100      # Used when food is not in PORTION_DB
DEFAULT_MULTIPLIER = 1.0 # Used when unit is not in UNIT_MULTIPLIERS


def estimate_portion(detected_foods: list) -> list:
    """
    Converts detected food items into gram-based portions.

    Input:
        [{"food": "rice", "quantity": 1, "unit": "bowl", "grams": 150}]
        Note: "grams" from Gemini is used if available and reasonable.

    Output:
        [{"food": "rice", "grams": 200}]
    """

    
    portions = []

    for item in detected_foods:
  
        food = item["food"]

       
        qty = item.get("quantity", 1)

      
        unit = item.get("unit", "unit").lower()

       
        gemini_grams = item.get("grams", 0)

        

        if gemini_grams and gemini_grams > 0:
           
            total = gemini_grams * qty

        else:
 
            base = PORTION_DB.get(food, DEFAULT_GRAMS)

           
            multiplier = UNIT_MULTIPLIERS.get(unit, DEFAULT_MULTIPLIER)


            total = base * multiplier * qty


        total = max(total, 1)

   
        portions.append({
            "food": food,
            "grams": round(total)
        })


    return portions