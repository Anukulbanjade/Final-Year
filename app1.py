import os
import logging
import re
import easyocr
import cv2
import numpy as np
from flask import Flask, render_template, request, jsonify
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
    reader = easyocr.Reader(['ne'], gpu=True)  # Use CPU if GPU is not available
    logger.info("EasyOCR reader initialized successfully")
except Exception as e:
    logger.error(f"Error initializing EasyOCR reader: {str(e)}")
    raise

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_nepali(text):
    """Check if text contains Devanagari characters (used in Nepali)"""
    devanagari_pattern = re.compile(r'[\u0900-\u097F]+')
    return bool(devanagari_pattern.search(text))

def process_nepali_text(text):
    """Clean and process the detected Nepali text"""
    if not text:
        return ""
    
    # Remove any unwanted characters
    text = text.strip()
    
    # Only keep text that contains Devanagari characters
    if not is_nepali(text):
        return ""
    
    return text

def enhance_image(image):
    """Enhance image for better text detection"""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                 cv2.THRESH_BINARY, 11, 2)
    
    # Denoise the image
    denoised = cv2.fastNlMeansDenoising(thresh)
    
    return denoised

def detect_text(image):
    try:
        # Ensure that the image is in the correct format
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:  # RGBA -> RGB
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)

        enhanced_image = enhance_image(image)

        # Try OCR on both the original and enhanced image
        results_original = reader.readtext(image)
        results_enhanced = reader.readtext(enhanced_image)
        
        all_results = results_original + results_enhanced
        detected_texts = []
        seen_texts = set()

        for (bbox, text, prob) in all_results:
            processed_text = process_nepali_text(text)
            if processed_text and processed_text not in seen_texts:
                seen_texts.add(processed_text)
                # Convert numpy types to native Python types
                bbox_list = [[float(point) for point in coord] for coord in bbox]
                detected_texts.append({
                    'text': processed_text,
                    'confidence': float(prob * 100),
                    'bbox': bbox_list
                })

        return detected_texts

    except Exception as e:
        logger.error(f"Error in text detection: {str(e)}")
        return []  # Return empty list to avoid breaking the app

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Handle image upload and text detection"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed types: png, jpg, jpeg, gif'}), 400

        # Read and process the image
        filestr = file.read()
        if not filestr:
            return jsonify({'error': 'No content in the file'}), 400
        npimg = np.frombuffer(filestr, np.uint8)
        image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        if image is None:
            return jsonify({'error': 'Failed to process image'}), 400

        # Detect text in the image
        results = detect_text(image)

        if not results:
            return jsonify({
                'warning': 'No Nepali characters detected in the image',
                'detections': []
            }), 200

        return jsonify({
            'success': True,
            'detections': results
        }), 200

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file size exceeded error"""
    return jsonify({'error': 'File size exceeded the limit (16MB)'}), 413

if __name__ == '__main__':
    app.run(debug=True)
