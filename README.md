# 🍱 Calories AI App (Food Intake & Calorie Intelligence)

## Live Demo

*(Add your deployed Streamlit/HuggingFace link here)*

---

## Objective

Calories AI is a lightweight web application that estimates calories and macronutrients from:

* Food images
* Meal videos
* Voice descriptions
* Text input

The goal is to reduce manual food logging while keeping results explainable and transparent.

---

## Features

### 1. Image Calorie Estimation

* Upload food image
* Detect food item
* Estimate portion size
* Output:

  * calories
  * protein/carbs/fat
  * confidence score
  * assumptions used

### 2. Video Meal Analysis

* Upload 10–30 sec video
* Frames sampled every few seconds
* Food detections aggregated
* Returns total calories and summary

### 3. Voice Logging

* Upload WAV audio
* Speech → text
* Extract food words
* Estimate calories

### 4. Text Logging

* Enter meal description
* Food extraction
* Nutrition summary

### 5. Explainability (Mandatory)

Each result shows:

* detected foods
* assumed portion size
* nutrition source
* confidence score
* disclaimer

---

## Tech Stack

Frontend/UI

* Streamlit

AI Components

* CNN food classifier
* Heuristic portion estimator
* Nutrition lookup dataset
* SpeechRecognition (voice)
* OpenCV (video frame sampling)

---

## Project Structure

```
project/
│
├── app.py
├── modules/
│   ├── image_detector.py
│   ├── portion.py
│   ├── calorie_calculator.py
│   ├── nutrition.py
│   ├── confidence.py
│   └── video_pipeline.py
│
├── data/
│   └── nutrition.csv
│
├── samples/
│   ├── images/
│   ├── videos/
│   └── audio/
```

---

## How to Run Locally

```
pip install -r requirements.txt
streamlit run app.py
```

Open browser:

```
http://localhost:8501
```

---

## Sample Inputs Included

* 10 sample images
* 3 sample videos
* 3 audio files

No external downloads required.

---

## Output Example

```
Detected: rice, egg
Calories: 425 kcal
Protein: 36g
Confidence: 82%
Assumption: standard serving size used
```

---

## Known Limitations

* Multi-food detection may miss overlapping foods
* Portion estimation is heuristic
* Not medical-grade accuracy
* Video aggregation may duplicate items

---

## Disclaimer

This app provides calorie estimates only.
Not medical or dietary advice.

---

## Future Improvements

* YOLO multi-food detection
* User history tracking
* Better portion estimation
* Barcode scanning

---

## Author

Atharva
Calories AI Project (Assignment Submission)
