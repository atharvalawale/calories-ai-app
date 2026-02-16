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

# Load nutrition DB once
load_nutrition_data()

SUPPORTED_FOODS = ['dal','egg','paneer','pizza','rice','roti','salad']

st.set_page_config(page_title="Calories AI", layout="centered")
st.title("🍱 Calories AI App")

tab1, tab2, tab3, tab4 = st.tabs([
    "Image",
    "Video",
    "Voice",
    "Text"
])

# =========================================================
# IMAGE TAB
# =========================================================
with tab1:
    st.header("Image calorie estimation")

    img = st.file_uploader("Upload food image", type=["jpg","png","jpeg"])
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

        foods = predict_food(path)

        # 🔥 ALWAYS CONTINUE PIPELINE
        portions = estimate_portion(foods)
        meal = calculate_meal_totals(portions)
        conf = compute_confidence(foods)

        st.subheader("Detected Food")
        st.json(foods)

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


# =========================================================
# VIDEO TAB
# =========================================================
with tab2:
    st.header("Video meal analysis")

    video = st.file_uploader("Upload video", type=["mp4","mov","avi"])

    if video:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(video.read())

        cap = cv2.VideoCapture(tfile.name)

        foods_all = []
        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % 60 == 0:
                frame_path = "frame.jpg"
                cv2.imwrite(frame_path, frame)

                foods = predict_food(frame_path)
                name = foods[0]["food"]

                exists = False
                for e in foods_all:
                    if e["food"] == name:
                        exists = True
                        break

                if not exists:
                    foods_all.append(foods[0])

            frame_count += 1

        cap.release()

        if foods_all:
            portions = estimate_portion(foods_all)
            meal = calculate_meal_totals(portions)
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
with tab3:
    st.header("Voice logging")

    audio = st.file_uploader("Upload WAV audio", type=["wav"])

    if audio:
        with open("temp.wav", "wb") as f:
            f.write(audio.read())

        r = sr.Recognizer()

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

                st.subheader("Meal Summary")
                st.json(meal)
            else:
                st.warning("No supported foods detected in speech.")

        except:
            st.error("Voice not recognized")

        st.info("Assumptions: Foods extracted from speech.")
        st.caption("⚠️ AI estimate only.")


# =========================================================
# TEXT TAB
# =========================================================
with tab4:
    st.header("Text logging")

    text = st.text_input("Enter meal description")

    if text:
        foods_raw = extract_food_items(text)

        foods = []
        for f in foods_raw:
            if f["food"] in SUPPORTED_FOODS:
                foods.append(f)

        if foods:
            portions = estimate_portion(foods)
            meal = calculate_meal_totals(portions)

            st.subheader("Detected Foods")
            st.json(foods)

            st.subheader("Meal Summary")
            st.json(meal)
        else:
            st.warning("No supported foods detected.")

        st.info("Assumptions: Portion estimated using default rules.")
        st.caption("⚠️ AI estimate only.")
