# retrain_model.py
import json
import numpy as np
from tensorflow.keras.models import load_model

# Load existing model and feedback data
model = load_model("models/devanagari_character_recognition_model_version1.keras")
feedback_data = []

# Read feedback data
with open("data/feedback_data.json", "r") as f:
    for line in f:
        feedback_data.append(json.loads(line))

# Example function to preprocess feedback data into model-ready format
# new_X, new_y = preprocess_feedback_data(feedback_data)

# # Re-train the model with new data
# model.fit(new_X, new_y, epochs=3)
# model.save("models/devanagari_character_recognition_model_version1.keras")
