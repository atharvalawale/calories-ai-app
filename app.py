import streamlit as st
import cv2
import tempfile
import speech_recognition as sr
import os
import math
from dotenv import load_dotenv

load_dotenv()

from modules.image_detector import predict_food
from modules.portion import estimate_portion
from modules.calorie_calculator import calculate_meal_totals
from modules.confidence import compute_confidence
from modules.nutrition import load_nutrition_data
from modules.text_parser import extract_food_items
from modules.health_score import compute_meal_health_score
from modules.personalization import apply_personalization
from modules.barcode import fetch_product
from modules.places import search_nearby_restaurants, search_restaurants_by_city
from modules.menu import get_menu_for_restaurant, get_item_by_id
from modules.cart import create_cart, add_to_cart, remove_from_cart, update_quantity, get_cart_meal_dict
from modules.order import process_order, format_order_confirmation
from modules.tracking import (
    calculate_daily_totals,
    get_goal_targets,
    generate_recommendation,
    calculate_streak,
    calculate_weekly_summary
)

# ===============================
# INITIAL SETUP
# ===============================

load_nutrition_data()

st.set_page_config(page_title="FoodMood", layout="centered")
st.title("🍱 FoodMood — AI Nutrition Assistant")

# ===============================
# SESSION STATE INIT
# ===============================

if "daily_log"   not in st.session_state: st.session_state.daily_log   = []
if "cart"        not in st.session_state: st.session_state.cart        = create_cart()
if "active_restaurant" not in st.session_state: st.session_state.active_restaurant = None
if "orders"      not in st.session_state: st.session_state.orders      = []
if "streak_log"  not in st.session_state: st.session_state.streak_log  = []
if "weekly_logs" not in st.session_state: st.session_state.weekly_logs = []

# ── Profile defaults ──────────────────────────────────────────────────────────
if "goal"           not in st.session_state: st.session_state.goal           = "maintenance"
if "allergies"      not in st.session_state: st.session_state.allergies      = []
if "name"           not in st.session_state: st.session_state.name           = ""
if "age"            not in st.session_state: st.session_state.age            = 25
if "weight_kg"      not in st.session_state: st.session_state.weight_kg      = 70
if "height_cm"      not in st.session_state: st.session_state.height_cm      = 170
if "gender"         not in st.session_state: st.session_state.gender         = "Male"
if "activity_level" not in st.session_state: st.session_state.activity_level = "Moderately Active"
if "diet_type"      not in st.session_state: st.session_state.diet_type      = "No restriction"

# ===============================
# BMI + TDEE CALCULATOR
# ===============================

def calculate_bmi(weight_kg: float, height_cm: float) -> tuple:
    """
    Calculates BMI and category.
    BMI = weight(kg) / height(m)^2

    WHY BMI:
    Quick indicator of healthy weight range
    Used by doctors and nutritionists worldwide
    """
    if height_cm <= 0:
        return 0, "Unknown"

    height_m = height_cm / 100
    bmi = round(weight_kg / (height_m ** 2), 1)

    if bmi < 18.5:   category = "Underweight 🔵"
    elif bmi < 25.0: category = "Normal ✅"
    elif bmi < 30.0: category = "Overweight 🟡"
    else:            category = "Obese 🔴"

    return bmi, category


def calculate_tdee(weight_kg: float, height_cm: float,
                   age: int, gender: str, activity_level: str) -> int:
    """
    Calculates Total Daily Energy Expenditure (TDEE).
    This is how many calories you need per day to maintain weight.

    WHY TDEE:
    Every person needs different calories based on their body
    A 90kg bodybuilder needs more calories than 50kg office worker
    TDEE = personalized calorie target

    Formula: Mifflin-St Jeor (most accurate for general population)
    Men:   BMR = 10*weight + 6.25*height - 5*age + 5
    Women: BMR = 10*weight + 6.25*height - 5*age - 161

    Then multiply by activity factor for TDEE
    """

    # Step 1: Calculate BMR (Basal Metabolic Rate)
    # BMR = calories needed just to stay alive (no movement)
    if gender == "Male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    # Step 2: Multiply by activity factor
    # WHY activity factor:
    # Sitting all day burns fewer calories than running marathons!
    activity_factors = {
        "Sedentary (desk job, no exercise)":     1.2,
        "Lightly Active (exercise 1-3 days/wk)": 1.375,
        "Moderately Active (exercise 3-5 days)": 1.55,
        "Very Active (exercise 6-7 days)":       1.725,
        "Extremely Active (athlete/hard labor)": 1.9,
    }

    factor = activity_factors.get(activity_level, 1.55)
    tdee   = round(bmr * factor)

    return tdee


# ===============================
# USER PROFILE SIDEBAR
# ===============================

st.sidebar.header("👤 User Profile")

# ── Personal Info ─────────────────────────────────────────────────────────────
st.sidebar.subheader("Personal Info")

st.session_state.name = st.sidebar.text_input(
    "Your Name", value=st.session_state.name,
    placeholder="Enter your name"
)

st.session_state.gender = st.sidebar.selectbox(
    "Gender",
    ["Male", "Female"],
    index=["Male", "Female"].index(st.session_state.gender)
)

st.session_state.age = st.sidebar.number_input(
    "Age", min_value=10, max_value=100,
    value=st.session_state.age, step=1
)

# ── Body Measurements ─────────────────────────────────────────────────────────
st.sidebar.subheader("Body Measurements")

st.session_state.weight_kg = st.sidebar.number_input(
    "Weight (kg)", min_value=30.0, max_value=300.0,
    value=float(st.session_state.weight_kg), step=0.5
)

st.session_state.height_cm = st.sidebar.number_input(
    "Height (cm)", min_value=100.0, max_value=250.0,
    value=float(st.session_state.height_cm), step=0.5
)

# ── Auto Calculate BMI ────────────────────────────────────────────────────────
bmi, bmi_category = calculate_bmi(
    st.session_state.weight_kg,
    st.session_state.height_cm
)

st.sidebar.metric("BMI", f"{bmi}", bmi_category)

# ── Activity Level ────────────────────────────────────────────────────────────
st.sidebar.subheader("Activity Level")

activity_options = [
    "Sedentary (desk job, no exercise)",
    "Lightly Active (exercise 1-3 days/wk)",
    "Moderately Active (exercise 3-5 days)",
    "Very Active (exercise 6-7 days)",
    "Extremely Active (athlete/hard labor)",
]

st.session_state.activity_level = st.sidebar.selectbox(
    "Activity Level",
    activity_options,
    index=activity_options.index(st.session_state.activity_level)
    if st.session_state.activity_level in activity_options else 2
)

# ── Auto Calculate TDEE ───────────────────────────────────────────────────────
tdee = calculate_tdee(
    st.session_state.weight_kg,
    st.session_state.height_cm,
    st.session_state.age,
    st.session_state.gender,
    st.session_state.activity_level
)

st.sidebar.metric("Daily Calorie Need (TDEE)", f"{tdee} kcal")

# ── Fitness Goal ──────────────────────────────────────────────────────────────
st.sidebar.subheader("Fitness Goal")

st.session_state.goal = st.sidebar.selectbox(
    "Your Goal",
    ["maintenance", "weight_loss", "muscle_gain"],
    index=["maintenance", "weight_loss", "muscle_gain"].index(st.session_state.goal)
)

# Show adjusted calorie target based on goal
# WHY adjustment:
# weight_loss  → eat 500 less than TDEE → lose ~0.5kg/week
# muscle_gain  → eat 300 more than TDEE → gain muscle
# maintenance  → eat exactly TDEE
goal_calories = {
    "maintenance":  tdee,
    "weight_loss":  tdee - 500,
    "muscle_gain":  tdee + 300,
}

adjusted_calories = goal_calories[st.session_state.goal]
st.sidebar.caption(f"🎯 Target calories: {adjusted_calories} kcal/day")

# ── Diet Type ─────────────────────────────────────────────────────────────────
st.sidebar.subheader("Diet Preferences")

diet_options = [
    "No restriction",
    "Vegetarian",
    "Vegan",
    "Keto",
    "Halal",
    "Gluten-free",
    "Diabetic-friendly",
]

st.session_state.diet_type = st.sidebar.selectbox(
    "Diet Type",
    diet_options,
    index=diet_options.index(st.session_state.diet_type)
    if st.session_state.diet_type in diet_options else 0
)

# ── Allergies ─────────────────────────────────────────────────────────────────
allergy_input = st.sidebar.text_input(
    "Allergies (comma separated)",
    placeholder="e.g. nuts, dairy, gluten"
)
st.session_state.allergies = [
    a.strip().lower() for a in allergy_input.split(",") if a.strip()
]

# ── Profile Summary ───────────────────────────────────────────────────────────
st.sidebar.divider()
st.sidebar.caption("📊 Profile Summary")
if st.session_state.name:
    st.sidebar.caption(f"👤 {st.session_state.name}")
st.sidebar.caption(f"⚖️ {st.session_state.weight_kg}kg | {st.session_state.height_cm}cm")
st.sidebar.caption(f"📊 BMI: {bmi} ({bmi_category})")
st.sidebar.caption(f"🔥 TDEE: {tdee} kcal")
st.sidebar.caption(f"🎯 Target: {adjusted_calories} kcal")
st.sidebar.caption(f"🥗 Diet: {st.session_state.diet_type}")

# ── Expose profile variables ──────────────────────────────────────────────────
goal      = st.session_state.goal
allergies = st.session_state.allergies

# ===============================
# SHARED HELPER
# ===============================

def display_meal_results(meal: dict, foods: list, key: str):
    """Shared UI block used by all tabs."""

    score, category, breakdown = compute_meal_health_score(meal)
    warnings, modifier = apply_personalization(meal, goal=goal, allergies=allergies)
    final_score = min(max(round(score + modifier, 1), 0), 100)

    st.subheader("Nutrition Summary")
    st.json(meal)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Health Score", f"{final_score} / 100")
    with col2:
        st.metric("Category", category)

    with st.expander("🔍 See what affected your score"):
        st.write("**What hurt your score (penalties):**")
        penalties = breakdown["penalties"]
        st.write(f"- Sugar: -{penalties['sugar']} points")
        st.write(f"- Sodium: -{penalties['sodium']} points")
        st.write(f"- Fat: -{penalties['fat']} points")
        st.write(f"- Calories: -{penalties['calories']} points")

        st.write("**What helped your score (rewards):**")
        rewards = breakdown["rewards"]
        st.write(f"- Protein: +{rewards['protein']} points")
        st.write(f"- Fiber: +{rewards['fiber']} points")

    if warnings:
        st.warning(warnings)

    if meal.get("skipped_foods"):
        st.info(f"Could not find nutrition data for: {', '.join(meal['skipped_foods'])}")

    if foods:
        conf = compute_confidence(foods)
        st.success(f"Model Confidence: {conf}%")

    if st.button("Add to Daily Log", key=key):
        st.session_state.daily_log.append(meal)
        st.success("Meal added to daily log!")

# ===============================
# TABS
# ===============================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📷 Image", "🎥 Video", "🎤 Voice", "📝 Text", "📦 Barcode", "📍 Places"
])

# =========================================================
# IMAGE TAB
# =========================================================

with tab1:
    st.header("Image calorie estimation")

    img     = st.file_uploader("Upload food image", type=["jpg", "png", "jpeg"])
    cam_img = st.camera_input("Or use live camera")
    path    = None

    if img:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(img.read())
            path = tmp.name
    elif cam_img:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(cam_img.read())
            path = tmp.name

    if path:
        st.image(path, use_container_width=True)
        with st.spinner("Analyzing image..."):
            foods = predict_food(path)

        if foods:
            st.subheader("Detected Foods")
            st.json(foods)
            portions = estimate_portion(foods)
            meal     = calculate_meal_totals(portions)
            display_meal_results(meal, foods, key="image_add")
        else:
            st.error("No food detected in image.")

        os.remove(path)
        st.caption("⚠️ AI estimate only.")

# =========================================================
# VIDEO TAB
# =========================================================

with tab2:
    st.header("Video meal analysis")
    video = st.file_uploader("Upload video", type=["mp4", "mov", "avi"])

    if video:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tfile:
            tfile.write(video.read())
            video_path = tfile.name

        cap        = cv2.VideoCapture(video_path)
        foods_all  = []
        frame_count = 0

        with st.spinner("Analyzing video frames..."):
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret: break
                if frame_count % 60 == 0:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as ffile:
                        frame_path = ffile.name
                    cv2.imwrite(frame_path, frame)
                    foods = predict_food(frame_path)
                    os.remove(frame_path)
                    if foods:
                        name = foods[0]["food"]
                        if not any(e["food"] == name for e in foods_all):
                            foods_all.append(foods[0])
                frame_count += 1

        cap.release()
        os.remove(video_path)

        if foods_all:
            portions = estimate_portion(foods_all)
            meal     = calculate_meal_totals(portions)
            display_meal_results(meal, foods_all, key="video_add")
        else:
            st.error("No food detected in video.")

# =========================================================
# VOICE TAB
# =========================================================

with tab3:
    st.header("Voice logging")
    audio = st.file_uploader("Upload WAV audio", type=["wav"])

    if audio:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio.read())
            wav_path = tmp.name

        r = sr.Recognizer()
        try:
            with sr.AudioFile(wav_path) as source:
                data = r.record(source)
            text = r.recognize_google(data)
            st.success(f"You said: {text}")
            with st.spinner("Extracting foods..."):
                foods = extract_food_items(text)
            if foods:
                portions = estimate_portion(foods)
                meal     = calculate_meal_totals(portions)
                display_meal_results(meal, foods, key="voice_add")
            else:
                st.warning("No food items detected in audio.")
        except sr.UnknownValueError:
            st.error("Voice not recognized. Please try again.")
        except Exception as e:
            st.error(f"Error processing audio: {e}")
        finally:
            os.remove(wav_path)

# =========================================================
# TEXT TAB
# =========================================================

with tab4:
    st.header("Text logging")
    text = st.text_input("Describe your meal (e.g. '2 eggs, bowl of rice, grilled chicken')")

    if text:
        with st.spinner("Analyzing meal..."):
            foods = extract_food_items(text)
        if foods:
            st.subheader("Detected Foods")
            st.json(foods)
            portions = estimate_portion(foods)
            meal     = calculate_meal_totals(portions)
            display_meal_results(meal, foods, key="text_add")
        else:
            st.warning("No food items detected. Try describing your meal differently.")

# =========================================================
# BARCODE TAB
# =========================================================

with tab5:
    st.header("Barcode Lookup")
    barcode = st.text_input("Enter product barcode (e.g. 3017620422003)")

    if barcode:
        with st.spinner("Looking up product..."):
            product = fetch_product(barcode)

        if "error" in product:
            st.error(f"Error: {product['error']}")
        else:
            st.json(product)
            meal = {
                "items": [{"food": product["name"],
                           "ingredients": product.get("ingredients", ""),
                           "allergens": product.get("allergens", [])}],
                "total_calories": product["calories_per_100g"],
                "total_protein":  product["protein_g"],
                "total_carbs":    product["carbs_g"],
                "total_fat":      product["fat_g"],
                "total_sugar":    product.get("sugar_g", 0),
                "total_sodium":   product.get("sodium_mg", 0),
                "skipped_foods":  [],
            }
            display_meal_results(meal, [], key="barcode_add")


# =========================================================
# PLACES TAB
# =========================================================

with tab6:
    st.header("📍 Nearby Restaurants")
    st.caption("Find restaurants, view menus and order food!")

    # ── View: Restaurant List or Menu or Cart or Checkout ─────────────────
    view = st.session_state.get("ordering_view", "restaurants")

    # ── BACK BUTTONS ──────────────────────────────────────────────────────
    if view == "menu":
        if st.button("← Back to Restaurants"):
            st.session_state.ordering_view = "restaurants"
            st.rerun()
    elif view in ["cart", "checkout", "confirmed"]:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back to Menu"):
                st.session_state.ordering_view = "menu"
                st.rerun()
        with col2:
            if st.button("🛒 Cart") and view != "cart":
                st.session_state.ordering_view = "cart"
                st.rerun()

    # ══════════════════════════════════════════════════════════════════════
    # VIEW 1 — RESTAURANT LIST
    # ══════════════════════════════════════════════════════════════════════
    if view == "restaurants":
        search_method = st.radio(
            "Search by:",
            ["City Name", "Coordinates"],
            horizontal=True
        )

        restaurants = []

        if search_method == "City Name":
            city = st.text_input(
                "Enter city name",
                placeholder="e.g. Mumbai, Pune, Delhi"
            )
            if city:
                with st.spinner(f"Finding restaurants in {city}..."):
                    restaurants = search_restaurants_by_city(city, limit=20)
        else:
            col1, col2 = st.columns(2)
            with col1:
                lat = st.number_input("Latitude",  value=19.0760, format="%.4f")
            with col2:
                lon = st.number_input("Longitude", value=72.8777, format="%.4f")
            if st.button("🔍 Search"):
                with st.spinner("Finding restaurants..."):
                    restaurants = search_nearby_restaurants(lat, lon, limit=20)

        if restaurants:
            st.success(f"Found {len(restaurants)} restaurants!")

            col1, col2 = st.columns(2)
            with col1:
                max_distance = st.slider("Max distance (km)", 0.5, 10.0, 5.0)
            with col2:
                cuisines = ["All"] + list(set(r["cuisine"] for r in restaurants))
                cuisine_filter = st.selectbox("Cuisine type", cuisines)

            filtered = [
                r for r in restaurants
                if r["distance_km"] <= max_distance
                and (cuisine_filter == "All" or r["cuisine"] == cuisine_filter)
            ]

            st.write(f"Showing {len(filtered)} restaurants")
            st.divider()

            for r in filtered:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.subheader(f"🍽️ {r['name']}")
                    st.write(f"📍 {r['address']}")
                    st.write(f"🍴 {r['cuisine'].title()}")
                    if r['phone']:
                        st.write(f"📞 {r['phone']}")
                with col2:
                    st.metric("Distance", f"{r['distance_km']} km")
                with col3:
                    if st.button("📋 Menu", key=f"menu_{r['name']}"):
                        st.session_state.active_restaurant = r
                        st.session_state.cart = create_cart()
                        st.session_state.cart["restaurant_name"] = r["name"]
                        st.session_state.ordering_view = "menu"
                        st.rerun()

                maps_url = f"https://www.google.com/maps?q={r['lat']},{r['lon']}"
                st.markdown(f"[📍 Open in Google Maps]({maps_url})")
                st.divider()

    # ══════════════════════════════════════════════════════════════════════
    # VIEW 2 — MENU
    # ══════════════════════════════════════════════════════════════════════
    elif view == "menu":
        restaurant = st.session_state.active_restaurant
        if not restaurant:
            st.error("No restaurant selected")
        else:
            st.subheader(f"🍽️ {restaurant['name']}")
            st.caption(f"📍 {restaurant['address']}")

            # Show cart summary at top
            cart = st.session_state.cart
            if cart["items"]:
                st.info(
                    f"🛒 {len(cart['items'])} items | "
                    f"₹{cart['total_price']} | "
                    f"{cart['total_calories']} kcal"
                )

            # Get menu for this cuisine
            menu_items = get_menu_for_restaurant(restaurant["cuisine"])

            # Filter options
            veg_only = st.checkbox("🌿 Veg only")
            if veg_only:
                menu_items = [i for i in menu_items if i["veg"]]

            st.divider()

            # Display menu items
            for item in menu_items:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"{item['image']} **{item['name']}**")
                    st.caption(item["description"])
                    st.caption(
                        f"🔥 {item['calories']} kcal | "
                        f"💪 {item['protein']}g protein | "
                        f"🍞 {item['carbs']}g carbs | "
                        f"🧈 {item['fat']}g fat"
                    )
                with col2:
                    st.write(f"**₹{item['price']}**")
                    if item["veg"]:
                        st.caption("🌿 Veg")
                    else:
                        st.caption("🍖 Non-veg")
                with col3:
                    if st.button("+ Add", key=f"add_{item['id']}"):
                        st.session_state.cart = add_to_cart(
                            st.session_state.cart, item
                        )
                        st.success(f"Added {item['name']}!")
                        st.rerun()
                st.divider()

            # Go to cart button
            if st.session_state.cart["items"]:
                if st.button(
                    f"🛒 View Cart ({len(st.session_state.cart['items'])} items) "
                    f"— ₹{st.session_state.cart['total_price']}",
                    type="primary"
                ):
                    st.session_state.ordering_view = "cart"
                    st.rerun()

    # ══════════════════════════════════════════════════════════════════════
    # VIEW 3 — CART
    # ══════════════════════════════════════════════════════════════════════
    elif view == "cart":
        st.subheader("🛒 Your Cart")
        cart = st.session_state.cart

        if not cart["items"]:
            st.warning("Your cart is empty!")
        else:
            st.caption(f"From: {cart['restaurant_name']}")
            st.divider()

            for item in cart["items"]:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"{item['image']} **{item['name']}**")
                    st.caption(
                        f"₹{item['price']} each | "
                        f"{item['calories']} kcal each"
                    )
                with col2:
                    new_qty = st.number_input(
                        "Qty",
                        min_value=0,
                        max_value=10,
                        value=item["quantity"],
                        key=f"qty_{item['id']}"
                    )
                    if new_qty != item["quantity"]:
                        st.session_state.cart = update_quantity(
                            st.session_state.cart,
                            item["id"],
                            new_qty
                        )
                        st.rerun()
                with col3:
                    st.write(f"₹{item['subtotal_price']}")
                    if st.button("🗑️", key=f"remove_{item['id']}"):
                        st.session_state.cart = remove_from_cart(
                            st.session_state.cart, item["id"]
                        )
                        st.rerun()

            st.divider()

            # Cart totals
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("Total",    f"₹{cart['total_price']}")
            with col2: st.metric("Calories", f"{cart['total_calories']} kcal")
            with col3: st.metric("Protein",  f"{cart['total_protein']}g")
            with col4: st.metric("Carbs",    f"{cart['total_carbs']}g")

            st.divider()

            if st.button("✅ Proceed to Checkout", type="primary"):
                st.session_state.ordering_view = "checkout"
                st.rerun()

    # ══════════════════════════════════════════════════════════════════════
    # VIEW 4 — CHECKOUT
    # ══════════════════════════════════════════════════════════════════════
    elif view == "checkout":
        st.subheader("💳 Checkout")
        cart = st.session_state.cart

        # Order summary
        st.write(f"**Order Total: ₹{cart['total_price']}**")
        st.write(f"🔥 Total Calories: {cart['total_calories']} kcal")
        st.divider()

        # Delivery details
        st.subheader("📦 Delivery Details")
        user_name        = st.text_input("Your Name", value=st.session_state.get("name", ""))
        phone            = st.text_input("Phone Number", placeholder="10 digit mobile number")
        delivery_address = st.text_area("Delivery Address", placeholder="Enter full address")

        st.divider()

        # Payment
        st.subheader("💳 Payment")
        payment_method = st.radio(
            "Payment Method",
            ["Demo (No real payment)", "Stripe (Real payment)"],
            horizontal=True
        )

        if payment_method == "Stripe (Real payment)":
            st.info(
                "🧪 Test card: 4242 4242 4242 4242 | "
                "Any future date | Any CVV"
            )

        st.divider()

        if st.button("🎉 Place Order", type="primary"):
            if not user_name or not phone or not delivery_address:
                st.error("Please fill all delivery details!")
            else:
                with st.spinner("Processing order..."):
                    use_stripe = (
                        payment_method == "Stripe (Real payment)"
                        and bool(os.environ.get("STRIPE_SECRET_KEY"))
                    )
                    order = process_order(
                        cart, user_name,
                        delivery_address, phone,
                        use_stripe=use_stripe
                    )

                if "error" not in order:
                    # Save order
                    st.session_state.orders.append(order)

                    # Auto log meal to daily log!
                    meal_dict = get_cart_meal_dict(cart)
                    st.session_state.daily_log.append(meal_dict)

                    # Clear cart
                    st.session_state.cart = create_cart()
                    st.session_state.ordering_view = "confirmed"
                    st.session_state.last_order = order
                    st.rerun()
                else:
                    st.error(f"Payment failed: {order.get('error')}")

    # ══════════════════════════════════════════════════════════════════════
    # VIEW 5 — ORDER CONFIRMED
    # ══════════════════════════════════════════════════════════════════════
    elif view == "confirmed":
        st.balloons()
        st.success("🎉 Order Placed Successfully!")

        order = st.session_state.get("last_order", {})
        if order:
            st.write(f"**Order ID:** {order['order_id']}")
            st.write(f"**Restaurant:** {order['restaurant']}")
            st.write(f"**Total:** ₹{order['total_price']}")
            st.write(f"**Calories:** {order['total_calories']} kcal")
            st.write(f"**Delivering to:** {order['delivery_address']}")

        st.info("✅ Meal automatically added to your daily nutrition log!")

        if st.button("🏠 Back to Restaurants"):
            st.session_state.ordering_view = "restaurants"
            st.rerun()


# =========================================================
# DAILY SUMMARY
# =========================================================

st.divider()
st.header("📊 Daily Nutrition Summary")

if st.session_state.daily_log:
    daily   = calculate_daily_totals(st.session_state.daily_log)
    targets = get_goal_targets(goal)

    # Override calorie target with TDEE-based target
    # WHY: TDEE is more accurate than our fixed targets
    targets["calories"] = adjusted_calories

    # Streak
    if not st.session_state.streak_log or st.session_state.streak_log[-1] != True:
        st.session_state.streak_log.append(True)

    streak = calculate_streak(st.session_state.streak_log)
    st.subheader(f"{streak['streak_emoji']} Streak: {streak['current_streak']} days in a row!")
    if streak['longest_streak'] > streak['current_streak']:
        st.caption(f"🏆 Best streak: {streak['longest_streak']} days")

    st.divider()

    # Progress bars
    st.subheader("📈 Today's Progress")

    def show_progress(label, actual, target, unit):
        pct   = min(actual / target, 1.0) if target > 0 else 0
        color = "✅" if pct >= 1.0 else "🟡" if pct >= 0.5 else "🔴"
        st.write(f"{color} **{label}:** {actual} / {target} {unit}")
        st.progress(pct)

    col1, col2 = st.columns(2)
    with col1:
        show_progress("Calories", daily.get("calories", 0), targets["calories"], "kcal")
        show_progress("Protein",  daily.get("protein",  0), targets["protein"],  "g")
        show_progress("Carbs",    daily.get("carbs",    0), targets["carbs"],    "g")
        show_progress("Fat",      daily.get("fat",      0), targets["fat"],      "g")
    with col2:
        show_progress("Fiber",    daily.get("fiber",    0), targets["fiber"],    "g")
        show_progress("Sugar",    daily.get("sugar",    0), targets["sugar"],    "g")
        show_progress("Sodium",   daily.get("sodium",   0), targets["sodium"],   "mg")

    st.divider()

    # AI Recommendation
    st.subheader("💡 AI Recommendation")
    recommendation = generate_recommendation(daily, goal)
    st.info(recommendation)

    st.divider()

    # Weekly Summary
    if len(st.session_state.weekly_logs) == 0 or st.session_state.weekly_logs[-1] != daily:
        st.session_state.weekly_logs.append(daily)
        if len(st.session_state.weekly_logs) > 7:
            st.session_state.weekly_logs = st.session_state.weekly_logs[-7:]

    if st.session_state.weekly_logs:
        weekly = calculate_weekly_summary(st.session_state.weekly_logs, goal)
        if weekly:
            st.subheader("📅 Weekly Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Days on Track", f"{weekly['days_goal_hit']} / {weekly['days_total']}")
            with col2:
                st.metric("Consistency", weekly['consistency'])
            with col3:
                st.metric("Avg Calories", f"{weekly['averages']['calories']} kcal")

    st.divider()

    if st.button("Clear Daily Log"):
        st.session_state.streak_log.append(False)
        st.session_state.daily_log = []
        st.rerun()
else:
    st.info("No meals logged yet today.")