# ─────────────────────────────────────────────────────────────────────────────
# places.py — Restaurant Discovery using TomTom API
# ─────────────────────────────────────────────────────────────────────────────
#
# WHY THIS FILE EXISTS:
# FoodMood needs to show nearby restaurants to users
# TomTom API is FREE, no credit card, no billing issues!
#
# HOW IT WORKS:
# 1. User enters location or uses coordinates
# 2. We search TomTom for nearby restaurants
# 3. Return list with name, address, rating, cuisine type
# ─────────────────────────────────────────────────────────────────────────────

import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOMTOM_API_KEY = os.environ.get("TOMTOM_API_KEY")
BASE_URL       = "https://api.tomtom.com/search/2"
TIMEOUT        = 5

# ── CATEGORY CODES ────────────────────────────────────────────────────────────
# WHY category codes:
# TomTom uses numbers to identify place types
# 7315 = restaurants (all types)
RESTAURANT_CATEGORY = "7315"


# ── FUNCTION 1: Search Nearby Restaurants ─────────────────────────────────────

def search_nearby_restaurants(
    lat: float,
    lon: float,
    radius: int = 2000,
    limit: int  = 20,
) -> list:
    """
    Searches for restaurants near given coordinates.

    Input:
        lat    = latitude  (e.g. 19.0760 for Mumbai)
        lon    = longitude (e.g. 72.8777 for Mumbai)
        radius = search radius in meters (default 2km)
        limit  = max results (default 20)

    Output:
        list of restaurant dicts
    """

    if not TOMTOM_API_KEY:
        print("TOMTOM_API_KEY not found in .env!")
        return []

    try:
        response = requests.get(
            f"{BASE_URL}/nearbySearch/.json",
            params={
                "lat":         lat,
                "lon":         lon,
                "radius":      radius,
                "categorySet": RESTAURANT_CATEGORY,
                "limit":       limit,
                "key":         TOMTOM_API_KEY,
            },
            timeout=TIMEOUT
        )

        if response.status_code != 200:
            print(f"TomTom API error: {response.status_code}")
            return []

        data    = response.json()
        results = data.get("results", [])

        restaurants = []
        for place in results:
            poi     = place.get("poi", {})
            address = place.get("address", {})
            pos     = place.get("position", {})
            dist    = place.get("dist", 0)

            restaurants.append({
                "name":       poi.get("name", "Unknown"),
                "address":    address.get("freeformAddress", ""),
                "lat":        pos.get("lat", lat),
                "lon":        pos.get("lon", lon),
                "distance_m": round(dist),
                "distance_km": round(dist / 1000, 1),
                "phone":      poi.get("phone", ""),
                "cuisine":    poi.get("categories", ["Restaurant"])[0]
                              if poi.get("categories") else "Restaurant",
                "url":        poi.get("url", ""),
            })

        print(f"Found {len(restaurants)} restaurants nearby")
        return restaurants

    except requests.Timeout:
        print("TomTom timeout — check internet connection")
        return []

    except Exception as e:
        print(f"TomTom error: {e}")
        return []


# ── FUNCTION 2: Search by City Name ───────────────────────────────────────────

def geocode_city(city: str) -> tuple:
    """
    Converts city name to coordinates.

    Input:  city name — "Mumbai", "Delhi", "Bangalore"
    Output: (lat, lon) tuple OR (None, None) if not found

    WHY needed:
    User types city name → we need coordinates for restaurant search
    """

    if not TOMTOM_API_KEY:
        return None, None

    try:
        response = requests.get(
            f"{BASE_URL}/geocode/{city}.json",
            params={"key": TOMTOM_API_KEY},
            timeout=TIMEOUT
        )

        if response.status_code != 200:
            return None, None

        data    = response.json()
        results = data.get("results", [])

        if not results:
            return None, None

        position = results[0].get("position", {})
        lat      = position.get("lat")
        lon      = position.get("lon")

        return lat, lon

    except Exception as e:
        print(f"Geocoding error: {e}")
        return None, None


# ── FUNCTION 3: Search Restaurants by City ────────────────────────────────────

def search_restaurants_by_city(city: str, limit: int = 20) -> list:
    """
    Searches restaurants by city name.

    Input:  city name string
    Output: list of restaurants

    Combines geocode + nearby search
    """

    lat, lon = geocode_city(city)

    if not lat or not lon:
        print(f"Could not find coordinates for: {city}")
        return []

    print(f"Searching restaurants in {city} ({lat}, {lon})")
    return search_nearby_restaurants(lat, lon, limit=limit)


# ── FUNCTION 4: Format Restaurant for Display ─────────────────────────────────

def format_restaurant(restaurant: dict) -> str:
    """Formats a restaurant dict for clean display."""

    return (
        f"🍽️ {restaurant['name']}\n"
        f"📍 {restaurant['address']}\n"
        f"🚶 {restaurant['distance_km']} km away\n"
        f"🍴 {restaurant['cuisine']}\n"
        f"📞 {restaurant['phone'] or 'N/A'}"
    )


# ── TEST ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Testing TomTom Places API")
    print("=" * 50)

    # Test 1 — Search by coordinates (Mumbai)
    print("\nTest 1: Restaurants near Mumbai")
    restaurants = search_nearby_restaurants(
        lat=19.0760, lon=72.8777, limit=5
    )
    for r in restaurants[:3]:
        print(format_restaurant(r))
        print()

    print("=" * 50)

    # Test 2 — Search by city name
    print("\nTest 2: Restaurants in Pune")
    restaurants2 = search_restaurants_by_city("Pune", limit=5)
    for r in restaurants2[:3]:
        print(format_restaurant(r))
        print()

    print(f"Total found: {len(restaurants2)}")