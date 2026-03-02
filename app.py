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
<<<<<<< HEAD
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

=======

# Load nutrition DB once
>>>>>>> 0b17e81dcefa826614e4d2c4e1e0748f61fcb827
load_nutrition_data()

SUPPORTED_FOODS = ['dal','egg','paneer','pizza','rice','roti','salad']

st.set_page_config(page_title="Calories AI", layout="centered")
st.title("🍱 Calories AI App")

<<<<<<< HEAD
# ===============================
# DAILY TRACKING INIT
# ===============================

if "daily_log" not in st.session_state:
    st.session_state.daily_log = []

# ===============================
# USER PROFILE
# ===============================

st.sidebar.header("User Profile")

goal = st.sidebar.selectbox(
    "Select your goal",
    ["maintenance", "weight_loss", "muscle_gain"]
)

allergy_input = st.sidebar.text_input(
    "Enter allergies (comma separated)",
    ""
)

allergies = [a.strip().lower() for a in allergy_input.split(",") if a.strip()]

# ===============================
# TABS
# ===============================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Image",
    "Video",
    "Voice",
    "Text",
    "Barcode"
=======
tab1, tab2, tab3, tab4 = st.tabs([
    "Image",
    "Video",
    "Voice",
    "Text"
>>>>>>> 0b17e81dcefa826614e4d2c4e1e0748f61fcb827
])

# =========================================================
# IMAGE TAB
# =========================================================
<<<<<<< HEAD

=======
>>>>>>> 0b17e81dcefa826614e4d2c4e1e0748f61fcb827
with tab1:
    st.header("Image calorie estimation")

    img = st.file_uploader("Upload food image", type=["jpg","png","jpeg"])
    cam_img = st.camera_input("Or use live camera")

    path = None

    if img:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(img.read())
            path = tmp.name
<<<<<<< HEAD
=======

>>>>>>> 0b17e81dcefa826614e4d2c4e1e0748f61fcb827
    elif cam_img:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(cam_img.read())
            path = tmp.name

    if path:
        st.image(path, use_column_width=True)

        foods = predict_food(path)
<<<<<<< HEAD
        portions = estimate_portion(foods)
        meal = calculate_meal_totals(portions)

        score, category = compute_meal_health_score(meal)
        warnings, modifier = apply_personalization(
            meal,
            goal=goal,
            allergies=allergies
        )

        final_score = max(score + modifier, 0)
=======

        # 🔥 ALWAYS CONTINUE PIPELINE
        portions = estimate_portion(foods)
        meal = calculate_meal_totals(portions)
>>>>>>> 0b17e81dcefa826614e4d2c4e1e0748f61fcb827
        conf = compute_confidence(foods)

        st.subheader("Detected Food")
        st.json(foods)

<<<<<<< HEAD
        st.subheader("Nutrition Summary")
        st.json(meal)

        st.subheader("Health Score")
        st.metric("Score", f"{final_score} / 100")
        st.write("Category:", category)

        if warnings:
            st.warning(warnings)

        st.success(f"Model Confidence: {conf}%")

        if st.button("Add to Daily Log", key="image_add"):
            st.session_state.daily_log.append(meal)
            st.success("Meal added to daily log!")

        os.remove(path)
        st.caption("⚠️ AI estimate only.")
=======
        # If low confidence → just warn (DO NOT STOP)
        if foods[0]["confidence"] < 50:
            st.warning("Low confidence prediction — calories estimated using best guess.")

        st.subheader("Portions")
        st.json(portions)

        st.subheader("Nutrition")
        st.json(meal)

        st.success(f"Confidence: {conf}%")

        os.remove(path)

        st.info("Assumptions: Portion estimated using heuristic rules and nutrition DB.")
        st.caption("⚠️ AI estimate only, not medical advice.")

>>>>>>> 0b17e81dcefa826614e4d2c4e1e0748f61fcb827

# =========================================================
# VIDEO TAB
# =========================================================
<<<<<<< HEAD

=======
>>>>>>> 0b17e81dcefa826614e4d2c4e1e0748f61fcb827
with tab2:
    st.header("Video meal analysis")

    video = st.file_uploader("Upload video", type=["mp4","mov","avi"])

    if video:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(video.read())

        cap = cv2.VideoCapture(tfile.name)
<<<<<<< HEAD
=======

>>>>>>> 0b17e81dcefa826614e4d2c4e1e0748f61fcb827
        foods_all = []
        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % 60 == 0:
                frame_path = "frame.jpg"
                cv2.imwrite(frame_path, frame)
<<<<<<< HEAD
                foods = predict_food(frame_path)
                name = foods[0]["food"]

                if not any(e["food"] == name for e in foods_all):
=======

                foods = predict_food(frame_path)
                name = foods[0]["food"]

                exists = False
                for e in foods_all:
                    if e["food"] == name:
                        exists = True
                        break

                if not exists:
>>>>>>> 0b17e81dcefa826614e4d2c4e1e0748f61fcb827
                    foods_all.append(foods[0])

            frame_count += 1

        cap.release()

        if foods_all:
            portions = estimate_portion(foods_all)
            meal = calculate_meal_totals(portions)
<<<<<<< HEAD

            score, category = compute_meal_health_score(meal)
            warnings, modifier = apply_personalization(meal, goal=goal, allergies=allergies)
            final_score = max(score + modifier, 0)
            conf = compute_confidence(foods_all)

            st.json(meal)
            st.metric("Health Score", f"{final_score} / 100")
            st.write("Category:", category)

            if warnings:
                st.warning(warnings)

            st.success(f"Model Confidence: {conf}%")

            if st.button("Add to Daily Log", key="video_add"):
                st.session_state.daily_log.append(meal)
                st.success("Meal added to daily log!")

        else:
            st.error("No food detected in video.")

# =========================================================
# VOICE TAB
# =========================================================

=======
            conf = compute_confidence(foods_all)

            st.subheader("Detected Foods")
            st.json(foods_all)

            st.subheader("Meal Summary")
            st.json(meal)

            st.success(f"Confidence: {conf}%")
        else:
            st.error("No food detected in video.")

        st.info("Assumptions: Foods aggregated from sampled frames.")
        st.caption("⚠️ AI estimate only.")


# =========================================================
# VOICE TAB
# =========================================================
>>>>>>> 0b17e81dcefa826614e4d2c4e1e0748f61fcb827
with tab3:
    st.header("Voice logging")

    audio = st.file_uploader("Upload WAV audio", type=["wav"])

    if audio:
        with open("temp.wav", "wb") as f:
            f.write(audio.read())

        r = sr.Recognizer()
<<<<<<< HEAD
=======

>>>>>>> 0b17e81dcefa826614e4d2c4e1e0748f61fcb827
        with sr.AudioFile("temp.wav") as source:
            data = r.record(source)

        try:
            text = r.recognize_google(data)
            st.success(f"You said: {text}")

            words = text.lower().split()
            foods = []

            for w in words:
                if w in SUPPORTED_FOODS:
                    foods.append({
                        "food": w,
                        "quantity": 1,
                        "unit": "unit",
                        "confidence": 80
                    })

            if foods:
                portions = estimate_portion(foods)
                meal = calculate_meal_totals(portions)

<<<<<<< HEAD
                score, category = compute_meal_health_score(meal)
                warnings, modifier = apply_personalization(meal, goal=goal, allergies=allergies)
                final_score = max(score + modifier, 0)

                st.json(meal)
                st.metric("Health Score", f"{final_score} / 100")

                if st.button("Add to Daily Log", key="voice_add"):
                    st.session_state.daily_log.append(meal)
                    st.success("Meal added to daily log!")

            else:
                st.warning("No supported foods detected.")
=======
                st.subheader("Meal Summary")
                st.json(meal)
            else:
                st.warning("No supported foods detected in speech.")
>>>>>>> 0b17e81dcefa826614e4d2c4e1e0748f61fcb827

        except:
            st.error("Voice not recognized")

<<<<<<< HEAD
# =========================================================
# TEXT TAB
# =========================================================

=======
        st.info("Assumptions: Foods extracted from speech.")
        st.caption("⚠️ AI estimate only.")


# =========================================================
# TEXT TAB
# =========================================================
>>>>>>> 0b17e81dcefa826614e4d2c4e1e0748f61fcb827
with tab4:
    st.header("Text logging")

    text = st.text_input("Enter meal description")

    if text:
        foods_raw = extract_food_items(text)
<<<<<<< HEAD
        foods = [f for f in foods_raw if f["food"] in SUPPORTED_FOODS]
=======

        foods = []
        for f in foods_raw:
            if f["food"] in SUPPORTED_FOODS:
                foods.append(f)
>>>>>>> 0b17e81dcefa826614e4d2c4e1e0748f61fcb827

        if foods:
            portions = estimate_portion(foods)
            meal = calculate_meal_totals(portions)

<<<<<<< HEAD
            score, category = compute_meal_health_score(meal)
            warnings, modifier = apply_personalization(meal, goal=goal, allergies=allergies)
            final_score = max(score + modifier, 0)

            st.json(meal)
            st.metric("Health Score", f"{final_score} / 100")

            if st.button("Add to Daily Log", key="text_add"):
                st.session_state.daily_log.append(meal)
                st.success("Meal added to daily log!")

        else:
            st.warning("No supported foods detected.")

# =========================================================
# BARCODE TAB
# =========================================================

with tab5:
    st.header("Barcode Lookup")

    barcode = st.text_input("Enter product barcode")

    if barcode:
        product = fetch_product(barcode)

        if product:
            st.json(product)

            meal = {
                "items": [],
                "total_calories": product["calories"],
                "total_protein": product["protein"],
                "total_carbs": product["carbs"],
                "total_fat": product["fat"],
                "total_sugar": product.get("sugar", 0),
                "total_sodium": product.get("sodium", 0)
            }

            score, category = compute_meal_health_score(meal)
            warnings, modifier = apply_personalization(meal, goal=goal, allergies=allergies)
            final_score = max(score + modifier, 0)

            st.metric("Health Score", f"{final_score} / 100")

            if st.button("Add to Daily Log", key="barcode_add"):
                st.session_state.daily_log.append(meal)
                st.success("Product added to daily log!")

        else:
            st.error("Product not found.")

# =========================================================
# DAILY SUMMARY
# =========================================================

st.divider()
st.header("📊 Daily Nutrition Summary")

if st.session_state.daily_log:

    daily = calculate_daily_totals(st.session_state.daily_log)
    targets = get_goal_targets(goal)

    st.write(f"Calories: {daily['calories']} / {targets['calories']}")
    st.progress(min(daily['calories'] / targets['calories'], 1.0))

    st.write(f"Protein: {daily['protein']}g / {targets['protein']}g")
    st.progress(min(daily['protein'] / targets['protein'], 1.0))

    st.write(f"Carbs: {daily['carbs']}g")
    st.write(f"Fat: {daily['fat']}g")

    recommendation = generate_recommendation(daily, targets)
    st.info(recommendation)

    if st.button("Clear Daily Log"):
        st.session_state.daily_log = []
        st.success("Daily log cleared!")

else:
    st.info("No meals logged yet today.")
=======
            st.subheader("Detected Foods")
            st.json(foods)

            st.subheader("Meal Summary")
            st.json(meal)
        else:
            st.warning("No supported foods detected.")

        st.info("Assumptions: Portion estimated using default rules.")
        st.caption("⚠️ AI estimate only.")
>>>>>>> 0b17e81dcefa826614e4d2c4e1e0748f61fcb827
