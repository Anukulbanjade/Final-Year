from flask import Flask, render_template, request, jsonify
import logging
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import easyocr
import cv2
import numpy as np
from werkzeug.utils import secure_filename
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize EasyOCR reader with Nepali support
try:
    reader = easyocr.Reader(['ne'], gpu=True)  # Use GPU for faster processing
    logger.info("EasyOCR reader initialized successfully")
except Exception as e:
    logger.error(f"Error initializing EasyOCR reader: {str(e)}")
    raise

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detect_text(image):
    """Detect Nepali text from an image using EasyOCR."""
    try:
        # Preprocess the image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
        _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)  # Binarize the image

        # Use EasyOCR to detect text
        results = reader.readtext(binary)
        logger.info(f"Raw OCR results: {results}")

        # Filter results for Nepali characters and convert to JSON-serializable format
        nepali_results = [
            {
                "text": text,
                "bbox": [list(map(float, point)) for point in bbox],  # Convert to float for JSON compatibility
                # "confidence": float(confidence)  # Convert to float
            }
            for bbox, text, confidence in results
            if any('\u0900' <= char <= '\u097F' for char in text)
        ]
        return nepali_results

    except Exception as e:
        logger.error(f"Error in text detection: {str(e)}")
        return []

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Handle image upload and process it for Nepali text detection."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Read the image
        image = cv2.imdecode(np.fromfile(filepath, np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            return jsonify({'error': 'Failed to process image'}), 400

        # Detect Nepali text
        detections = detect_text(image)

        if not detections:
            return jsonify({'warning': 'No Nepali characters detected in the image', 'detections': []}), 200

        return jsonify({'success': True, 'detections': detections}), 200

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file size exceeded error."""
    return jsonify({'error': 'File size exceeded the limit (16MB)'}), 413

if __name__ == '__main__':
    app.run(debug=True)