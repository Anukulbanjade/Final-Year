from flask import Flask, send_from_directory, request, jsonify, send_file
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import cv2
import numpy as np
from werkzeug.utils import secure_filename
import easyocr
from gtts import gTTS
import uuid

# Initialize Flask app
app = Flask(__name__, static_folder='frontend/build', static_url_path='')

# Allowed file types and upload configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['AUDIO_FOLDER'] = 'audio'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['AUDIO_FOLDER'], exist_ok=True)

# Initialize EasyOCR reader
reader = easyocr.Reader(['ne'], gpu=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detect_text(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    results = reader.readtext(binary)
    nepali_results = [
        {"text": text, "bbox": [list(map(float, point)) for point in bbox]}
        for bbox, text, confidence in results
        if any('\u0900' <= char <= '\u097F' for char in text)
    ]
    return nepali_results

def generate_nepali_audio(text):
    # Generate a unique filename
    audio_filename = f"{uuid.uuid4()}.mp3"
    audio_filepath = os.path.join(app.config['AUDIO_FOLDER'], audio_filename)
    
    # Use gTTS to generate Nepali audio
    # Note: gTTS supports Nepali through the 'ne' language code
    try:
        tts = gTTS(text=text, lang='ne')
        tts.save(audio_filepath)
        return audio_filename
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None

# Serve the React app
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# API endpoint for predictions
@app.route('/predict', methods=['POST'])
def predict():
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
    
    image = cv2.imdecode(np.fromfile(filepath, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        return jsonify({'error': 'Failed to process image'}), 400
    
    detections = detect_text(image)
    
    # Generate audio for the first detected Nepali text
    audio_filename = None
    if detections:
        first_text = detections[0]['text']
        audio_filename = generate_nepali_audio(first_text)
    
    return jsonify({
        'success': True, 
        'detections': detections,
        'audio': audio_filename
    }), 200

# Endpoint to serve generated audio files
@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_file(
        os.path.join(app.config['AUDIO_FOLDER'], filename), 
        mimetype='audio/mp3'
    )

# Fallback route for React routing
@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)