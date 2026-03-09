import streamlit as st
import cv2
import tempfile
import speech_recognition as sr
import os

from modules.image_detector import predict_food
from modules.portion import estimate_portion
from modules.calorie_calculator import calculate_meal_totals
from modules.confidence import compute_confidence
from modules.nutrition import load_nutrition_data
from modules.text_parser import extract_food_items
from modules.health_score import compute_meal_health_score
from modules.personalization import apply_personalization
from modules.barcode import fetch_product
from modules.tracking import (
    calculate_daily_totals,
    get_goal_targets,
    generate_recommendation
)

# ===============================
# INITIAL SETUP
# ===============================

load_nutrition_data()

st.set_page_config(page_title="Calories AI", layout="centered")
st.title("🍱 Calories AI App")

# ===============================
# SESSION STATE INIT
# ===============================

if "daily_log" not in st.session_state:
    st.session_state.daily_log = []

if "goal" not in st.session_state:
    st.session_state.goal = "maintenance"

if "allergies" not in st.session_state:
    st.session_state.allergies = []

# ===============================
# USER PROFILE (persisted in session)
# ===============================

st.sidebar.header("User Profile")

st.session_state.goal = st.sidebar.selectbox(
    "Select your goal",
    ["maintenance", "weight_loss", "muscle_gain"],
    index=["maintenance", "weight_loss", "muscle_gain"].index(st.session_state.goal)
)

allergy_input = st.sidebar.text_input("Enter allergies (comma separated)", "")
st.session_state.allergies = [a.strip().lower() for a in allergy_input.split(",") if a.strip()]

goal = st.session_state.goal
allergies = st.session_state.allergies

# ===============================
# SHARED HELPER
# ===============================

def display_meal_results(meal: dict, foods: list, key: str):
    """Shared UI block used by all tabs."""
    score, category = compute_meal_health_score(meal)
    warnings, modifier = apply_personalization(meal, goal=goal, allergies=allergies)
    final_score = max(score + modifier, 0)

    st.subheader("Nutrition Summary")
    st.json(meal)

    st.metric("Health Score", f"{final_score} / 100")
    st.write("Category:", category)

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

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Image", "Video", "Voice", "Text", "Barcode"
])

# =========================================================
# IMAGE TAB
# =========================================================

with tab1:
    st.header("Image calorie estimation")

    img = st.file_uploader("Upload food image", type=["jpg", "png", "jpeg"])
    cam_img = st.camera_input("Or use live camera")

    path = None

    if img:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(img.read())
            path = tmp.name
    elif cam_img:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(cam_img.read())
            path = tmp.name

    if path:
        st.image(path, use_column_width=True)

        with st.spinner("Analyzing image..."):
            foods = predict_food(path)

        if foods:
            st.subheader("Detected Foods")
            st.json(foods)

            portions = estimate_portion(foods)
            meal = calculate_meal_totals(portions)
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

        cap = cv2.VideoCapture(video_path)
        foods_all = []
        frame_count = 0

        with st.spinner("Analyzing video frames..."):
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % 60 == 0:
                    # Use tempfile instead of hardcoded "frame.jpg"
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
            meal = calculate_meal_totals(portions)
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
                foods = extract_food_items(text)  # now uses Claude — works for any food

            if foods:
                portions = estimate_portion(foods)
                meal = calculate_meal_totals(portions)
                display_meal_results(meal, foods, key="voice_add")
            else:
                st.warning("No food items detected in audio.")

        except sr.UnknownValueError:
            st.error("Voice not recognized. Please try again.")
        except Exception as e:
            st.error(f"Error processing audio: {e}")
        finally:
            os.remove(wav_path)  # always clean up

# =========================================================
# TEXT TAB
# =========================================================

with tab4:
    st.header("Text logging")

    text = st.text_input("Describe your meal (e.g. '2 eggs, bowl of rice, grilled chicken')")

    if text:
        with st.spinner("Analyzing meal..."):
            foods = extract_food_items(text)  # now uses Claude — no 9-food limit

        if foods:
            st.subheader("Detected Foods")
            st.json(foods)

            portions = estimate_portion(foods)
            meal = calculate_meal_totals(portions)
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

            # Use updated field names from fixed barcode.py
            meal = {
                "items": [{
                    "food": product["name"],
                    "ingredients": product.get("ingredients", ""),
                    "allergens": product.get("allergens", []),
                }],
                "total_calories": product["calories_per_100g"],
                "total_protein": product["protein_g"],
                "total_carbs": product["carbs_g"],
                "total_fat": product["fat_g"],
                "total_sugar": product.get("sugar_g", 0),
                "total_sodium": product.get("sodium_mg", 0),
                "skipped_foods": [],
            }

            display_meal_results(meal, [], key="barcode_add")

# =========================================================
# DAILY SUMMARY
# =========================================================

st.divider()
st.header("📊 Daily Nutrition Summary")

if st.session_state.daily_log:
    daily = calculate_daily_totals(st.session_state.daily_log)
    targets = get_goal_targets(goal)

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Calories:** {daily['calories']} / {targets['calories']} kcal")
        st.progress(min(daily['calories'] / targets['calories'], 1.0))

        st.write(f"**Protein:** {daily['protein']}g / {targets['protein']}g")
        st.progress(min(daily['protein'] / targets['protein'], 1.0))

    with col2:
        st.write(f"**Carbs:** {daily['carbs']}g")
        st.write(f"**Fat:** {daily['fat']}g")
        st.write(f"**Sugar:** {daily.get('sugar', 0)}g")
        st.write(f"**Sodium:** {daily.get('sodium', 0)}mg")

    recommendation = generate_recommendation(daily, targets)
    st.info(recommendation)

    if st.button("Clear Daily Log"):
        st.session_state.daily_log = []
        st.rerun()
else:
    st.info("No meals logged yet today.")