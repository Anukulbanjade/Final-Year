import React, { useState } from 'react';
import './App.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUpload, faCheckCircle, faSearch } from '@fortawesome/free-solid-svg-icons';

function App() {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [progress, setProgress] = useState(false);
    const [prediction, setPrediction] = useState("");
    const [processedImage, setProcessedImage] = useState("");

    // Detect if the user is on a mobile device
    const isMobileDevice = () => /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);

    // Handle file selection and preview
    const handleFileChange = (event) => {
        const selectedFile = event.target.files[0];
        setFile(selectedFile);
    };

    // Handle form submission
    const handleSubmit = async (event) => {
        event.preventDefault();
        if (!file) {
            alert("Please upload an image first.");
            return;
        }

        setLoading(false);
        setProgress(true);
        setPrediction("");
        setProcessedImage("");

        // Show progress bar for 3 seconds, then start actual processing
        setTimeout(async () => {
            setProgress(false);
            setLoading(true);

            const formData = new FormData();
            formData.append("image", file); // Send original image

            try {
                const response = await fetch("http://localhost:5000/predict", {
                    method: "POST",
                    body: formData,
                });
                const data = await response.json();

                if (data.predicted_class) {
                    setPrediction(data.predicted_class);
                    setProcessedImage(`data:image/png;base64,${data.processed_image}`);
                } else {
                    alert("Prediction failed: " + data.error);
                }
            } catch (error) {
                console.error("Error:", error);
                alert("An error occurred while processing the image.");
            } finally {
                setLoading(false);
            }
        }, 3000);  // Progress bar duration of 3 seconds
    };

    return (
        <div className="App">
            <h1>देवनागरी अक्षर पहिचान प्रणाली</h1>
            <p>Upload an image of a handwritten Devanagari character to recognize it.</p>

            <form onSubmit={handleSubmit} className="upload-form">
                <input 
                    type="file" 
                    accept="image/*" 
                    capture={isMobileDevice() ? "environment" : undefined} 
                    onChange={handleFileChange} 
                    id="file-input" 
                    hidden 
                />
                <label htmlFor="file-input" className={`upload-button ${file ? "active" : ""}`}>
                    <FontAwesomeIcon icon={faUpload} /> Choose Image
                </label>
                <button type="submit" className="submit-button">
                    <FontAwesomeIcon icon={faSearch} /> Recognize
                </button>
            </form>

            {progress && (
                <div className="progress-overlay">
                    <div className="progress-text">Processing<span className="dots">...</span></div>
                    <div className="progress-bar-container">
                        <div className="progress-bar"></div>
                    </div>
                </div>
            )}

            {loading && (
                <div className="loader">Processing...</div>
            )}

            {prediction && (
                <div className="result-section">
                    <h2>Result</h2>
                    <p className="prediction-text">
                        <FontAwesomeIcon icon={faCheckCircle} /> Predicted Character: {prediction}
                    </p>
                    {processedImage && (
                        <div>
                            <h3>Processed Image</h3>
                            <img src={processedImage} alt="Processed" />
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default App;
