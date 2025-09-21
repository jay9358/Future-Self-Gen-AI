import React, { useState } from 'react';
import axios from 'axios';

const API_URL = 'https://striking-bravery-production.up.railway.app/api';

const PhotoUpload = ({ onPhotoUpload, onNext, onSkip }) => {
  const [uploadedImage, setUploadedImage] = useState(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileUpload = async (files) => {
    if (files.length === 0) return;
    
    const file = files[0];
    if (!file.type.startsWith('image/')) {
      alert('Please upload an image file');
      return;
    }
    
    if (file.size > 5 * 1024 * 1024) {
      alert('File size must be less than 5MB');
      return;
    }
    
    // Preview image
    const reader = new FileReader();
    reader.onload = (e) => {
      setUploadedImage(e.target.result);
    };
    reader.readAsDataURL(file);
    
    // Upload to server
    const formData = new FormData();
    formData.append('photo', file);
    
    setIsUploading(true);
    try {
      const response = await axios.post(`${API_URL}/upload`, formData);
      
      if (response.data.success) {
        onPhotoUpload(response.data);
        console.log('Photo uploaded successfully');
      } else {
        alert('Upload failed: ' + (response.data.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed. Server may not be running.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    handleFileUpload(e.dataTransfer.files);
  };

  return (
    <div className="step active">
      <h2>Step 1: Upload Your Photo</h2>
      <p>Upload a clear front-facing photo of yourself</p>
      
      <div 
        className="upload-area"
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={() => document.getElementById('photoInput').click()}
      >
        <div className="upload-icon">📸</div>
        <h3>Click or Drag Photo Here</h3>
        <p>JPG, PNG up to 5MB</p>
        <input 
          type="file" 
          id="photoInput" 
          accept="image/*" 
          style={{ display: 'none' }}
          onChange={(e) => handleFileUpload(e.target.files)}
        />
      </div>

      {uploadedImage && (
        <div style={{ textAlign: 'center', margin: '20px 0' }}>
          <img 
            src={uploadedImage} 
            alt="Uploaded" 
            style={{ maxWidth: '300px', borderRadius: '15px' }}
          />
          <div className="button-group">
            <button 
              className="btn" 
              onClick={onNext}
              disabled={isUploading}
            >
              {isUploading ? 'Uploading...' : 'Next: Upload Resume'}
            </button>
            <button 
              className="btn btn-secondary" 
              onClick={onSkip}
              disabled={isUploading}
            >
              Skip Resume
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default PhotoUpload;
