"use client";

import { useState, useRef } from 'react';

// Define the shape of our form data
interface FormQuestion {
  id: number;
  question: string;
  answer: string;
}

export default function AudioUploadForm() {
  // ===== STATE MANAGEMENT =====
  
  // Form data state - same as your original component
  const [formData, setFormData] = useState<FormQuestion[]>([
    { id: 1, question: "Ask me anything?", answer: "" },
  ]);

  // Loading states for different operations
  const [loading, setLoading] = useState(false);
  const [audioLoading, setAudioLoading] = useState(false);
  const [fileLoading, setFileLoading] = useState(false);
  
  // Response and error handling
  const [response, setResponse] = useState<any>(null);
  const [error, setError] = useState('');

  // ===== AUDIO RECORDING STATES =====
  
  // Track if we're currently recording
  const [isRecording, setIsRecording] = useState(false);
  
  // Store the recorded audio blob
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  
  // Store the audio URL for playback
  const [audioUrl, setAudioUrl] = useState<string>('');
  
  // Reference to MediaRecorder object
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  
  // Store audio chunks during recording
  const audioChunksRef = useRef<Blob[]>([]);

  // ===== FILE UPLOAD STATES =====
  
  // Store selected file
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  
  // Reference to file input element (hidden)
  const fileInputRef = useRef<HTMLInputElement>(null);

  // ===== FORM HANDLING FUNCTIONS =====
  
  // Handle text input changes (same as original)
  const handleInputChange = (id: number, value: string) => {
    setFormData(prev => 
      prev.map(item => 
        item.id === id ? { ...item, answer: value } : item
      )
    );
  };

  // ===== AUDIO RECORDING FUNCTIONS =====
  
  // Start recording audio
  const startRecording = async () => {
    try {
      // Request microphone permission
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: true 
      });
      
      // Create MediaRecorder instance
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      
      // Clear previous audio chunks
      audioChunksRef.current = [];
      
      // Handle data available event (when recording stops)
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      // Handle recording stop event
      mediaRecorder.onstop = () => {
        // Create blob from all audio chunks
        const audioBlob = new Blob(audioChunksRef.current, { 
          type: 'audio/wav' 
        });
        
        // Create URL for audio playback
        const audioUrl = URL.createObjectURL(audioBlob);
        
        // Update state
        setAudioBlob(audioBlob);
        setAudioUrl(audioUrl);
        
        // Stop all tracks to release microphone
        stream.getTracks().forEach(track => track.stop());
      };
      
      // Start recording
      mediaRecorder.start();
      setIsRecording(true);
      setError(''); // Clear any previous errors
      
    } catch (err) {
      setError('Failed to access microphone. Please check permissions.');
      console.error('Recording error:', err);
    }
  };

  // Stop recording audio
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  // Clear recorded audio
  const clearAudio = () => {
    setAudioBlob(null);
    setAudioUrl('');
    // Clean up the URL to prevent memory leaks
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
    }
  };

  // ===== FILE HANDLING FUNCTIONS =====
  
  // Handle file selection when user picks a file
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setError(''); // Clear any previous errors
    }
  };

  // Trigger file picker when button is clicked
  const openFilePicker = () => {
    fileInputRef.current?.click();
  };

  // Remove selected file
  const removeFile = () => {
    setSelectedFile(null);
    // Reset the file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // ===== AUDIO UPLOAD FUNCTION =====
  
  // Upload audio file to backend
  const uploadAudio = async () => {
    if (!audioBlob) {
      setError('No audio recorded');
      return;
    }

    setAudioLoading(true);
    setError('');

    try {
      // Create FormData object (like a form submission)
      const formData = new FormData();
      
      // Add audio file to form data
      // Creates a file with name "recording.wav"
      formData.append('file', audioBlob, 'recording.wav');

      // Send POST request to your FastAPI backend
      const response = await fetch('http://0.0.0.0:8000/upload-file/', { //ahiya api for audio upload
        method: 'POST',
        body: formData, // Send form data (not JSON)
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Audio upload success:', result);
        
        // Show success message
        setResponse({
          type: 'audio_upload',
          data: result
        });
        
        // Optionally clear the audio after successful upload
        // clearAudio();
        
      } else {
        throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
      }
      
    } catch (err) {
      setError(`Audio upload error: ${err instanceof Error ? err.message : 'Unknown error'}`);
      console.error('Audio upload error:', err);
    } finally {
      setAudioLoading(false);
    }
  };

  // Upload selected file to backend
  const uploadFile = async () => {
    if (!selectedFile) {
      setError('Please select a file first');
      return;
    }

    setFileLoading(true);
    setError('');

    try {
      // Create FormData object (like a form submission)
      const formData = new FormData();
      
      // Add selected file to form data
      // The key 'file' matches your FastAPI endpoint parameter
      formData.append('file', selectedFile);

      // Send POST request to your FastAPI backend
      const response = await fetch('http://0.0.0.0:8000/upload-file/', { //here add api for file upload probably same
        method: 'POST',
        body: formData, // Send form data (not JSON)
      });

      if (response.ok) {
        const result = await response.json();
        console.log('File upload success:', result);
        
        // Show success message with file info
        setResponse({
          type: 'file_upload',
          data: result
        });
        
        // Optionally clear the file after successful upload
        // removeFile();
        
      } else {
        throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
      }
      
    } catch (err) {
      setError(`File upload error: ${err instanceof Error ? err.message : 'Unknown error'}`);
      console.error('File upload error:', err);
    } finally {
      setFileLoading(false);
    }
  };

  // ===== TEXT FORM SUBMISSION (Original functionality) =====
  
  const handleSubmit = async () => {
    setLoading(true);
    setError('');
    setResponse(null);

    // Validate form
    const hasEmptyAnswers = formData.some(item => !item.answer.trim());
    if (hasEmptyAnswers) {
      setError('Please fill in all fields');
      setLoading(false);
      return;
    }

    try {
      const apiResponse = await fetch('http://0.0.0.0:8000/generate_slide', { // add api for text form (probbaly the same api key and id)
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ data: formData }),
      });

      if (apiResponse.ok) {
        const result = await apiResponse.json();
        setResponse({
          type: 'text_submission',
          data: result
        });
        console.log('API Response:', result);
      } else {
        throw new Error(`API Error: ${apiResponse.status} ${apiResponse.statusText}`);
      }
    } catch (err) {
      setError(`Error: ${err instanceof Error ? err.message : 'Unknown error'}`);
      console.error('API Request Error:', err);
    } finally {
      setLoading(false);
    }
  };

  // ===== RENDER COMPONENT =====
  
  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h1 className="text-3xl font-bold text-gray-800 mb-6 text-center">
        Audio Recording & Text Form
      </h1>
      
      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {/* Response Display */}
      {response && (
        <div className="mb-6 p-4 bg-green-100 border border-green-400 text-green-700 rounded">
          <h3 className="font-bold mb-2">
            {response.type === 'audio_upload' ? 'Audio Upload Response:' : 
             response.type === 'file_upload' ? 'File Upload Response:' : 'Text Form Response:'}
          </h3>
          <pre className="text-sm overflow-x-auto">
            {JSON.stringify(response.data, null, 2)}
          </pre>
        </div>
      )}

      {/* ===== AUDIO RECORDING SECTION ===== */}
      <div className="mb-8 p-4 border-2 border-blue-200 rounded-lg bg-blue-50">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">🎤 Audio Recording</h2>
        
        {/* Recording Controls */}
        <div className="flex gap-3 mb-4">
          {!isRecording ? (
            <button
              onClick={startRecording}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md font-medium transition-colors duration-200"
              disabled={audioLoading}
            >
              🔴 Start Recording
            </button>
          ) : (
            <button
              onClick={stopRecording}
              className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md font-medium transition-colors duration-200 animate-pulse"
            >
              ⏹️ Stop Recording
            </button>
          )}
          
          {audioBlob && (
            <button
              onClick={clearAudio}
              className="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-md font-medium transition-colors duration-200"
              disabled={audioLoading}
            >
              🗑️ Clear Audio
            </button>
          )}
        </div>

        {/* Recording Status */}
        {isRecording && (
          <div className="mb-4 p-3 bg-red-100 border border-red-300 text-red-700 rounded flex items-center">
            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse mr-2"></div>
            Recording in progress... Click "Stop Recording" when done.
          </div>
        )}

        {/* Audio Playback */}
        {audioUrl && (
          <div className="mb-4">
            <p className="text-sm text-gray-600 mb-2">✅ Audio recorded successfully! Play it back:</p>
            <audio controls className="w-full">
              <source src={audioUrl} type="audio/wav" />
              Your browser does not support audio playback.
            </audio>
          </div>
        )}

        {/* Upload Button */}
        {audioBlob && (
          <button
            onClick={uploadAudio}
            disabled={audioLoading}
            className={`w-full py-3 px-4 rounded-md font-medium text-white transition-colors duration-200 ${
              audioLoading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2'
            }`}
          >
            {audioLoading ? (
              <div className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Uploading Audio...
              </div>
            ) : (
              '🚀 Upload Audio to Backend'
            )}
          </button>
        )}
      </div>

      {/* ===== FILE UPLOAD SECTION ===== */}
      <div className="mb-8 p-4 border-2 border-purple-200 rounded-lg bg-purple-50">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">📁 File Upload</h2>
        
        {/* Hidden file input - this opens when button is clicked */}
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileSelect}
          className="hidden"
          accept="*/*" // Accept all file types, your backend handles conversion
        />
        
        {/* File selection area */}
        <div className="mb-4">
          {!selectedFile ? (
            // No file selected - show select button
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <p className="text-gray-500 mb-3">No file selected</p>
              <button
                onClick={openFilePicker}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-md font-medium transition-colors duration-200"
                disabled={fileLoading}
              >
                📎 Choose File
              </button>
            </div>
          ) : (
            // File selected - show file info
            <div className="border border-gray-300 rounded-lg p-4 bg-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-800">Selected File:</p>
                  <p className="text-sm text-gray-600">{selectedFile.name}</p>
                  <p className="text-xs text-gray-500">
                    Size: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
                <button
                  onClick={removeFile}
                  className="px-3 py-1 bg-red-500 hover:bg-red-600 text-white rounded text-sm"
                  disabled={fileLoading}
                >
                  ❌ Remove
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Upload button - only show when file is selected */}
        {selectedFile && (
          <button
            onClick={uploadFile}
            disabled={fileLoading}
            className={`w-full py-3 px-4 rounded-md font-medium text-white transition-colors duration-200 ${
              fileLoading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2'
            }`}
          >
            {fileLoading ? (
              <div className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Uploading File...
              </div>
            ) : (
              '🚀 Upload File to Backend'
            )}
          </button>
        )}

        {/* Supported file types info */}
        <div className="mt-3 text-xs text-gray-500">
          <p>💡 Supported: Images (HEIC→JPG), Excel (XLS/XLSX→CSV), Office docs (PPTX/PPT/ODT→PDF), and more!</p>
        </div>
      </div>

      {/* ===== TEXT FORM SECTION (Original) ===== */}
      <div className="mb-6 p-4 border-2 border-gray-200 rounded-lg">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">📝 Text Form</h2>
        
        <div className="space-y-6">
          {formData.map((item) => (
            <div key={item.id} className="space-y-2">
              <label className="block text-sm font-medium text-black-700">
                {item.question}
              </label>
              <textarea
                value={item.answer}
                onChange={(e) => handleInputChange(item.id, e.target.value)}
                className="w-full px-2 py-1 text-sm text-black border border-black rounded-md shadow-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 resize-none"
                rows={2}
                placeholder="Enter your answer here..."
                disabled={loading}
              />
            </div>
          ))}

          <button
            onClick={handleSubmit}
            disabled={loading}
            className={`w-full py-3 px-4 rounded-md font-medium text-white transition-colors duration-200 ${
              loading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
            }`}
          >
            {loading ? (
              <div className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Sending Request...
              </div>
            ) : (
              'Generate Slides'
            )}
          </button>
        </div>
      </div>

      {/* Debug Info */}
      <div className="mt-6 text-sm text-gray-500">
        <h3 className="font-semibold mb-2">Request Format Preview:</h3>
        <pre className="bg-gray-100 p-3 rounded text-xs overflow-x-auto">
        {JSON.stringify({ data: formData }, null, 2)}
        </pre>
      </div>
    </div>
  );
}