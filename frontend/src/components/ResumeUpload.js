import React, { useState } from 'react';
import axios from 'axios';

const API_URL = 'https://ideal-youth-production.up.railway.app/api';

const ResumeUpload = ({ sessionId, onResumeUpload, onBack, onNext }) => {
  const [resumeAnalysis, setResumeAnalysis] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleFileUpload = async (files) => {
    if (files.length === 0) return;
    
    const file = files[0];
    const formData = new FormData();
    formData.append('resume', file);
    formData.append('career_goal', 'software_engineer'); // Default career goal
    
    setIsAnalyzing(true);
    try {
      const response = await axios.post(`${API_URL}/analyze-resume`, formData);
      
      if (response.data.success) {
        setResumeAnalysis(response.data);
        onResumeUpload(response.data);
      }
    } catch (error) {
      console.error('Resume upload error:', error);
      alert('Failed to analyze resume');
    } finally {
      setIsAnalyzing(false);
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
      <h2>Step 2: Upload Your Resume (Optional)</h2>
      <p>Get personalized career recommendations based on your experience</p>
      
      <div 
        className="upload-area"
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={() => document.getElementById('resumeInput').click()}
      >
        <div className="upload-icon">📄</div>
        <h3>Upload Resume</h3>
        <p>PDF, DOCX, or TXT format</p>
        <input 
          type="file" 
          id="resumeInput" 
          accept=".pdf,.docx,.txt" 
          style={{ display: 'none' }}
          onChange={(e) => handleFileUpload(e.target.files)}
        />
      </div>

      {resumeAnalysis && (
        <div className="resume-analysis">
          <h3>Resume Analysis</h3>
          <div>
            <h4>Skills Detected:</h4>
            <div className="skills-tags">
              {(resumeAnalysis.extracted_info?.skills || []).map((skill, index) => (
                <span key={index} className="skill-tag">{skill}</span>
              ))}
            </div>
          </div>
          <div>
            <p>Experience: <strong>{resumeAnalysis.extracted_info?.years_experience || 0} years</strong></p>
          </div>
          <div className="career-matches">
            <h4>Career Match Analysis:</h4>
            <div className="career-match-item">
              <strong>Match Percentage: {resumeAnalysis.career_match?.match_percentage || 0}%</strong>
              <span className="match-score">Career Readiness: {resumeAnalysis.career_match?.career_readiness || 'Unknown'}</span>
            </div>
            {resumeAnalysis.career_match?.matched_skills && (
              <div>
                <h5>Matched Skills:</h5>
                <div className="skills-tags">
                  {resumeAnalysis.career_match.matched_skills.slice(0, 5).map((skill, index) => (
                    <span key={index} className="skill-tag matched">{skill}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="button-group">
        <button className="btn btn-secondary" onClick={onBack}>Back</button>
        <button 
          className="btn" 
          onClick={onNext}
          disabled={isAnalyzing}
        >
          {isAnalyzing ? 'Analyzing...' : 'Next: Choose Career'}
        </button>
      </div>
    </div>
  );
};

export default ResumeUpload;
