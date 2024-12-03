import React, { useState, useRef } from 'react';
import { Upload, Copy, Check, Image, Loader2, Sparkles, Volume2, XCircle, FileType, Scale, Palette, Pause } from 'lucide-react';

const App = () => {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [detections, setDetections] = useState([]);
  const [combinedText, setCombinedText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [preview, setPreview] = useState('');
  const [processingStep, setProcessingStep] = useState(0);
  const [copiedIndex, setCopiedIndex] = useState(null);
  const [audioSrc, setAudioSrc] = useState(null);
  const [isAudioPlaying, setIsAudioPlaying] = useState(false);
  const audioRef = useRef(null);

  const processingSteps = [
    { icon: FileType, text: 'Analyzing image format...' },
    { icon: Scale, text: 'Processing dimensions...' },
    { icon: Palette, text: 'Enhancing contrast...' },
    { icon: Sparkles, text: 'Detecting characters...' }
  ];

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setMessage('');
      setDetections([]);
      setPreview(URL.createObjectURL(selectedFile));
      setAudioSrc(null);
    }
  };

  const handleCopy = async (text, index) => {
    await navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const handleCopyAll = async () => {
    await navigator.clipboard.writeText(combinedText);
    setCopiedIndex(-1);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const toggleAudioPlayback = () => {
    if (audioRef.current) {
      if (isAudioPlaying) {
        audioRef.current.pause();
        setIsAudioPlaying(false);
      } else {
        audioRef.current.play();
        setIsAudioPlaying(true);
      }
    }
  };

  const handleAudioEnded = () => {
    setIsAudioPlaying(false);
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage('Please select an image to begin detection');
      return;
    }

    setIsLoading(true);
    setMessage('');
    setDetections([]);
    setAudioSrc(null);

    for (let i = 0; i < processingSteps.length; i++) {
      setProcessingStep(i);
      await new Promise(resolve => setTimeout(resolve, 800));
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      
      if (data.success) {
        setDetections(data.detections);
        const combinedDetectedText = data.detections.map(item => item.text).join('\n');
        setCombinedText(combinedDetectedText);
        
        if (data.audio) {
          setAudioSrc(`/audio/${data.audio}`);
        }
      } else {
        setMessage(data.warning || 'No text detected. Please try a different image.');
      }
    } catch (error) {
      setMessage('Upload failed. Please try again.');
      console.error('Upload Error:', error);
    } finally {
      setIsLoading(false);
      setProcessingStep(0);
    }
  };

  return (
    <div className="min-h-screen p-4 md:p-8 bg-gradient-to-br from-[#e6f2ff] to-[#b3d9ff]">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white/90 backdrop-blur-lg rounded-xl shadow-2xl border border-gray-200 overflow-hidden">
          <header className="px-6 py-5 border-b border-gray-200 bg-gray-900/10">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-gray-800">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Devanagari Text Detection</h1>
                <p className="mt-1 text-sm text-gray-700">AI-Powered Text Recognition System</p>
              </div>
            </div>
          </header>

          <div className="p-6">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <div className="border-2 border-dashed rounded-xl border-gray-300 relative group">
                  <label className="flex flex-col items-center justify-center h-64 cursor-pointer overflow-hidden">
                    <input type="file" accept="image/*" onChange={handleFileChange} className="sr-only" />
                    {preview ? (
                      <>
                        <img src={preview} alt="Preview" className="h-full w-full object-cover rounded-lg" />
                        <div className="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                          <p className="text-white text-sm font-medium">Change Image</p>
                        </div>
                      </>
                    ) : (
                      <div className="text-center p-6">
                        <div className="w-16 h-16 mx-auto rounded-full flex items-center justify-center bg-gray-800">
                          <Image className="w-8 h-8 text-white" />
                        </div>
                        <div className="mt-4">
                          <span className="text-sm font-medium text-gray-900">Drop image here</span>
                          <p className="mt-1 text-xs text-gray-600">PNG, JPG up to 10MB</p>
                        </div>
                      </div>
                    )}
                  </label>
                </div>

                <button
                  onClick={handleUpload}
                  disabled={isLoading || !file}
                  className="mt-4 w-full flex items-center justify-center gap-2 text-white px-4 py-3 rounded-lg font-medium
                           disabled:opacity-50 disabled:cursor-not-allowed transition-all
                           bg-gray-900 hover:bg-gray-800 shadow-lg"
                >
                  {isLoading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <>
                      <Upload className="w-5 h-5" />
                      Process Image
                    </>
                  )}
                </button>
              </div>

              <div>
                {detections.length > 0 && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <h2 className="text-lg font-medium text-gray-900 flex items-center gap-2">
                        <Sparkles className="w-5 h-5 text-gray-800" />
                        Detected Text
                      </h2>
                      <div className="flex items-center gap-2">
                        {audioSrc && (
                          <button 
                            onClick={toggleAudioPlayback} 
                            className="text-xs text-white px-2 py-1 rounded-full bg-gray-900 hover:bg-gray-800 transition-colors flex items-center gap-1"
                          >
                            {isAudioPlaying ? (
                              <>
                                <Pause className="w-4 h-4" />
                                Pause
                              </>
                            ) : (
                              <>
                                <Volume2 className="w-4 h-4" />
                                Listen
                              </>
                            )}
                          </button>
                        )}
                        <button 
                          onClick={handleCopyAll} 
                          className="text-xs text-white px-2 py-1 rounded-full bg-gray-900 hover:bg-gray-800 transition-colors"
                        >
                          {copiedIndex === -1 ? 'Copied!' : 'Copy All'}
                        </button>
                      </div>
                    </div>
                    <textarea 
                      readOnly 
                      value={combinedText}
                      className="w-full h-64 p-4 bg-gray-100 border border-gray-200 rounded-lg resize-none"
                      placeholder="Detected text will appear here..."
                    />
                    
                    <div className="space-y-2 max-h-[200px] overflow-y-auto pr-2">
                      {detections.map((item, index) => (
                        <div
                          key={index}
                          className="group flex items-center gap-3 bg-gray-100 hover:bg-gray-200 p-4 rounded-lg border border-gray-200 transition-all"
                        >
                          <div className="flex-1">
                            <p className="text-sm text-gray-900 font-medium">{item.text}</p>
                            {item.confidence && (
                              <div className="flex items-center gap-1.5 mt-1">
                                <div className="h-1 w-16 bg-gray-300 rounded-full overflow-hidden">
                                  <div 
                                    className="h-full rounded-full bg-gray-800"
                                    style={{ width: `${item.confidence}%` }}
                                  />
                                </div>
                                <span className="text-xs text-gray-600">{item.confidence}%</span>
                              </div>
                            )}
                          </div>
                          <button
                            onClick={() => handleCopy(item.text, index)}
                            className="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-200 transition-colors"
                          >
                            {copiedIndex === index ? (
                              <Check className="w-4 h-4 text-green-600" />
                            ) : (
                              <Copy className="w-4 h-4" />
                            )}
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {!detections.length && !isLoading && (
                  <div className="h-64 flex flex-col items-center justify-center text-gray-500 bg-gray-100 rounded-lg border border-gray-200">
                    <Image className="w-12 h-12 mb-3 text-gray-400" />
                    <p className="text-sm">Upload an image to begin detection</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {audioSrc && (
            <audio 
              ref={audioRef} 
              src={audioSrc} 
              onEnded={handleAudioEnded} 
              className="hidden" 
            />
          )}

          {isLoading && (
            <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center">
              <div className="bg-white/90 backdrop-blur-md p-8 rounded-xl border border-gray-200 max-w-md w-full mx-4">
                <div className="flex items-center justify-center mb-6">
                  {processingSteps.map((step, index) => (
                    <div key={index} className="flex items-center">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        index === processingStep ? 'bg-gray-300' : 
                        index < processingStep ? 'bg-gray-900' : 'bg-gray-200'
                      }`}>
                        {index < processingStep ? (
                          <Check className="w-4 h-4 text-white" />
                        ) : (
                          <step.icon className={`w-4 h-4 ${
                            index === processingStep ? 'text-gray-900' : 'text-gray-400'
                          }`} />
                        )}
                      </div>
                      {index < processingSteps.length - 1 && (
                        <div className={`w-12 h-0.5 ${
                          index < processingStep ? 'bg-gray-900' : 'bg-gray-200'
                        }`} />
                      )}
                    </div>
                  ))}
                </div>
                <p className="text-center text-gray-900 font-medium">
                  {processingSteps[processingStep].text}
                </p>
                <div className="mt-4 w-full h-1 bg-gray-200 rounded-full overflow-hidden">
                  <div className="h-full rounded-full animate-[progressFill_2s_ease-in-out_infinite] bg-gray-900" />
                </div>
              </div>
            </div>
          )}

          <footer className="px-6 py-4 border-t border-gray-200 bg-gray-900/10">
            <p className="text-xs text-gray-600 text-center">
              © 2024 Devanagari Text Detection • Enhanced with AI Technology
            </p>
          </footer>
        </div>
      </div>
    </div>
  );
};

export default App;