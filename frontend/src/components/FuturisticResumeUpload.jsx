import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardHeader, CardBody, CardTitle, CardDescription, Button, Badge, SkillBadge, ProgressBar } from './ui';
import axios from 'axios';
import { API_CONFIG } from '../config/api';

const FuturisticResumeUpload = ({ sessionId, onResumeUpload, onBack, onNext }) => {
  const [resumeAnalysis, setResumeAnalysis] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);

  const handleFileUpload = async (files) => {
    if (files.length === 0) return;
    
    const file = files[0];
    
    // Validate file type
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    if (!allowedTypes.includes(file.type)) {
      setError('Please upload a PDF, DOCX, or TXT file');
      return;
    }

    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB');
      return;
    }
    
    const formData = new FormData();
    formData.append('resume', file);
    formData.append('career_goal', 'software_engineer');
    
    setIsAnalyzing(true);
    setUploadProgress(0);
    setError(null);
    
    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      const response = await axios.post(API_CONFIG.ENDPOINTS.ANALYZE_RESUME, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 30000, // 30 second timeout
      });
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      if (response.data.success) {
        setResumeAnalysis(response.data);
        onResumeUpload(response.data);
      } else {
        setError(response.data.error || 'Analysis failed');
      }
    } catch (error) {
      console.error('Resume upload error:', error);
      if (error.response?.data?.error) {
        setError(error.response.data.error);
      } else if (error.code === 'ECONNABORTED') {
        setError('Request timeout. Please try again.');
      } else if (error.message?.includes('Network Error')) {
        setError('Network error. Please check your connection and try again.');
      } else {
        setError('Failed to analyze resume. Please check your connection and try again.');
      }
    } finally {
      setIsAnalyzing(false);
      setTimeout(() => setUploadProgress(0), 1000);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    handleFileUpload(e.dataTransfer.files);
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="max-w-4xl mx-auto p-6"
    >
      <Card variant="glass" glow className="overflow-hidden">
        <CardHeader>
          <div className="text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-cyan-400 to-purple-500 rounded-2xl flex items-center justify-center"
            >
              <span className="text-2xl">📄</span>
            </motion.div>
            <CardTitle className="text-2xl">Resume Analysis</CardTitle>
            <CardDescription className="text-lg">
              Upload your resume to get personalized career insights from your future self
            </CardDescription>
          </div>
        </CardHeader>

        <CardBody>
          {/* Error Display */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg"
            >
              <div className="flex items-center space-x-2">
                <span className="text-red-400">⚠️</span>
                <span className="text-red-400">{error}</span>
              </div>
            </motion.div>
          )}

          {/* Upload Area */}
          <motion.div
            whileHover={{ scale: 1.02 }}
            className={`
              relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 cursor-pointer
              ${dragActive 
                ? 'border-cyan-400 bg-cyan-500/10' 
                : 'border-white/30 hover:border-cyan-400/50 hover:bg-white/5'
              }
              ${isAnalyzing ? 'pointer-events-none' : ''}
            `}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => !isAnalyzing && document.getElementById('resumeInput').click()}
          >
            <input 
              type="file" 
              id="resumeInput" 
              accept=".pdf,.docx,.txt" 
              style={{ display: 'none' }}
              onChange={(e) => handleFileUpload(e.target.files)}
            />
            
            <AnimatePresence>
              {!isAnalyzing ? (
                <motion.div
                  key="upload"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="space-y-4"
                >
                  <div className="text-6xl mb-4">📁</div>
                  <h3 className="text-xl font-semibold text-white">
                    Drop your resume here
                  </h3>
                  <p className="text-white/60">
                    PDF, DOCX, or TXT format • Max 10MB
                  </p>
                  <Button variant="secondary" size="lg">
                    Choose File
                  </Button>
                </motion.div>
              ) : (
                <motion.div
                  key="analyzing"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="space-y-6"
                >
                  <div className="text-6xl mb-4">🔍</div>
                  <h3 className="text-xl font-semibold text-white">
                    Analyzing your resume...
                  </h3>
                  <ProgressBar 
                    value={uploadProgress} 
                    variant="primary" 
                    size="lg"
                    label="Processing"
                  />
                  <p className="text-white/60">
                    AI is extracting skills, experience, and career insights
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>

          {/* Analysis Results */}
          <AnimatePresence>
            {resumeAnalysis && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.5 }}
                className="mt-8 space-y-6"
              >
                {/* Skills Section */}
                <Card variant="dark">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <span>🎯</span>
                      <span>Skills Detected</span>
                      <Badge variant="primary" size="sm">
                        {(resumeAnalysis.extracted_info?.skills || []).length}
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardBody>
                    <div className="flex flex-wrap gap-2">
                      {(resumeAnalysis.extracted_info?.skills || []).map((skill, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, scale: 0.8 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: index * 0.1 }}
                        >
                          <SkillBadge skill={skill} level="intermediate" />
                        </motion.div>
                      ))}
                    </div>
                  </CardBody>
                </Card>

                {/* Experience Section */}
                <Card variant="dark">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <span>💼</span>
                      <span>Experience Analysis</span>
                    </CardTitle>
                  </CardHeader>
                  <CardBody>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div className="text-center">
                        <div className="text-3xl font-bold text-cyan-400">
                          {resumeAnalysis.extracted_info?.years_experience || 0}
                        </div>
                        <div className="text-sm text-white/60">Years Experience</div>
                      </div>
                      <div className="text-center">
                        <div className="text-3xl font-bold text-purple-400">
                          {resumeAnalysis.career_match?.match_percentage || 0}%
                        </div>
                        <div className="text-sm text-white/60">Career Match</div>
                      </div>
                      <div className="text-center">
                        <div className="text-3xl font-bold text-green-400">
                          {resumeAnalysis.career_match?.career_readiness || 'Unknown'}
                        </div>
                        <div className="text-sm text-white/60">Readiness Level</div>
                      </div>
                    </div>
                  </CardBody>
                </Card>

                {/* Career Insights */}
                {resumeAnalysis.career_match?.matched_skills && (
                  <Card variant="accent" glow>
                    <CardHeader>
                      <CardTitle className="flex items-center space-x-2">
                        <span>🚀</span>
                        <span>Career Insights</span>
                      </CardTitle>
                    </CardHeader>
                    <CardBody>
                      <div className="space-y-4">
                        <div>
                          <h4 className="font-semibold text-white mb-2">Matched Skills:</h4>
                          <div className="flex flex-wrap gap-2">
                            {resumeAnalysis.career_match.matched_skills.slice(0, 8).map((skill, index) => (
                              <Badge key={index} variant="success" size="sm">
                                {skill}
                              </Badge>
                            ))}
                          </div>
                        </div>
                        
                        {resumeAnalysis.career_match?.missing_skills && resumeAnalysis.career_match.missing_skills.length > 0 && (
                          <div>
                            <h4 className="font-semibold text-white mb-2">Skills to Develop:</h4>
                            <div className="flex flex-wrap gap-2">
                              {resumeAnalysis.career_match.missing_skills.slice(0, 5).map((skill, index) => (
                                <Badge key={index} variant="warning" size="sm">
                                  {skill}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </CardBody>
                  </Card>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </CardBody>

        {/* Action Buttons */}
        <div className="p-6 border-t border-white/10">
          <div className="flex justify-between">
            <Button variant="secondary" onClick={onBack}>
              Back
            </Button>
            <Button 
              onClick={onNext}
              disabled={isAnalyzing || !resumeAnalysis}
              className="min-w-[120px]"
            >
              {isAnalyzing ? 'Analyzing...' : 'Next: Choose Career'}
            </Button>
          </div>
        </div>
      </Card>
    </motion.div>
  );
};

export default FuturisticResumeUpload;