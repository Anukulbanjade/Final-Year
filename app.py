from flask import Flask, request, jsonify, render_template
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image

app = Flask(__name__)

# Load the model
model = load_model("devanagari_character_recognition_model_version1.keras")

# Home route to render the HTML template
@app.route('/')
def home():
    return render_template('index.html')

# Define the prediction route
@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    # Read the image file
    file = request.files['image']
    img = Image.open(file).convert('L')  # Convert to grayscale
    img = img.resize((32, 32))           # Resize to match model input

    # Preprocess the image
    img_array = np.array(img) / 255.0    # Normalize
    img_array = img_array.reshape(1, 32, 32, 1)  # Reshape to model's input shape

    # Make a prediction
    prediction = model.predict(img_array)
    predicted_class = np.argmax(prediction, axis=1)[0]

    return jsonify({"predicted_class": int(predicted_class)})

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
