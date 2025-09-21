import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Navbar, Card, CardHeader, CardBody, CardTitle, CardDescription, Button } from './components/ui';
import FuturisticResumeUpload from './components/FuturisticResumeUpload';
import FuturisticChat from './components/FuturisticChat';
import FuturisticDashboard from './components/FuturisticDashboard';
import axios from 'axios';
import './App.css';

const API_URL = 'http://localhost:5000/api';

function App() {
  const [currentStep, setCurrentStep] = useState('welcome');
  const [sessionId, setSessionId] = useState(null);
  const [resumeAnalysis, setResumeAnalysis] = useState(null);
  const [persona, setPersona] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Debug logging
  useEffect(() => {
    console.log('App State:', { currentStep, sessionId, hasPersona: !!persona });
  }, [currentStep, sessionId, persona]);

  const handleResumeUpload = (data) => {
    console.log('Resume upload response:', data);
    
    // The resume analysis endpoint returns session_id and persona
    if (data.success && data.session_id) {
      setSessionId(data.session_id); // Update sessionId from resume response
      setResumeAnalysis(data);
      setPersona(data.persona);
      
      // Log for debugging
      console.log('Updated state with:', {
        sessionId: data.session_id,
        persona: data.persona
      });
      
      // Move to dashboard
      setCurrentStep('dashboard');
    } else {
      setError('Failed to process resume. Missing session or persona.');
      console.error('Invalid resume response:', data);
    }
  };

  const handleStartChat = () => {
    // Verify we have required data before starting chat
    if (!sessionId || !persona) {
      console.error('Cannot start chat:', { sessionId, persona });
      setError('Please upload your resume first');
      setCurrentStep('resume');
      return;
    }
    
    console.log('Starting chat with:', { sessionId, persona: persona.name });
    setCurrentStep('chat');
  };

  const handleBack = () => {
    if (currentStep === 'chat') {
      setCurrentStep('dashboard');
    } else if (currentStep === 'dashboard') {
      setCurrentStep('resume');
    } else {
      setCurrentStep('welcome');
    }
  };

  const handleNext = () => {
    if (currentStep === 'welcome') {
      setCurrentStep('resume');
    } else if (currentStep === 'resume' && resumeAnalysis) {
      setCurrentStep('dashboard');
    } else if (currentStep === 'dashboard' && sessionId && persona) {
      setCurrentStep('chat');
    }
  };

  const renderWelcome = () => (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.8 }}
      className="min-h-screen flex items-center justify-center p-6"
    >
      <div className="max-w-4xl mx-auto text-center">
        {/* Hero Section */}
        <motion.div
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.8 }}
          className="mb-12"
        >
          <div className="w-24 h-24 mx-auto mb-8 bg-gradient-to-br from-cyan-400 to-purple-500 rounded-3xl flex items-center justify-center">
            <span className="text-4xl">🔮</span>
          </div>
          <h1 className="text-6xl md:text-7xl font-bold text-white mb-6">
            Future Self
          </h1>
          <p className="text-xl md:text-2xl text-white/70 mb-8 max-w-3xl mx-auto">
            Connect with your future self and discover the career path that awaits you. 
            Get personalized guidance from the person you'll become in 10 years.
          </p>
        </motion.div>

        {/* Features Grid */}
        <motion.div
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.8 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12"
        >
          <Card variant="glass" glow className="text-center">
            <CardBody>
              <div className="text-4xl mb-4">📄</div>
              <CardTitle>Resume Analysis</CardTitle>
              <CardDescription>
                AI-powered analysis of your skills, experience, and career potential
              </CardDescription>
            </CardBody>
          </Card>

          <Card variant="glass" glow className="text-center">
            <CardBody>
              <div className="text-4xl mb-4">💬</div>
              <CardTitle>Future Chat</CardTitle>
              <CardDescription>
                Chat with your future self and get personalized career guidance
              </CardDescription>
            </CardBody>
          </Card>

          <Card variant="glass" glow className="text-center">
            <CardBody>
              <div className="text-4xl mb-4">🚀</div>
              <CardTitle>Career Insights</CardTitle>
              <CardDescription>
                Discover your career path and unlock your full potential
              </CardDescription>
            </CardBody>
          </Card>
        </motion.div>

        {/* CTA Section */}
        <motion.div
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.6, duration: 0.8 }}
          className="space-y-6"
        >
          <Button 
            size="xl" 
            onClick={handleNext}
            className="px-12 py-4 text-xl"
          >
            Start Your Journey
          </Button>
          <p className="text-white/60">
            Upload your resume to begin your personalized future self experience
          </p>
        </motion.div>
      </div>
    </motion.div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900">
      {/* Background Effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl" />
      </div>

      {/* Navbar */}
      <Navbar 
        isConnected={!!sessionId && !!persona} 
        onConnect={() => setCurrentStep('resume')} 
      />

      {/* Main Content */}
      <div className="relative z-10">
        {/* Error Display */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="fixed top-20 right-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg z-50"
          >
            <div className="flex items-center space-x-2">
              <span className="text-red-400">⚠️</span>
              <span className="text-red-400">{error}</span>
              <button 
                onClick={() => setError(null)}
                className="ml-4 text-red-400 hover:text-red-300"
              >
                ✕
              </button>
            </div>
          </motion.div>
        )}

        <AnimatePresence mode="wait">
          {currentStep === 'welcome' && (
            <motion.div
              key="welcome"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              {renderWelcome()}
            </motion.div>
          )}

          {currentStep === 'resume' && (
            <motion.div
              key="resume"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              <FuturisticResumeUpload
                sessionId={sessionId}
                onResumeUpload={handleResumeUpload}
                onBack={handleBack}
                onNext={() => {
                  if (resumeAnalysis) {
                    setCurrentStep('dashboard');
                  } else {
                    setError('Please upload and analyze your resume first');
                  }
                }}
              />
            </motion.div>
          )}

          {currentStep === 'dashboard' && (
            <motion.div
              key="dashboard"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              <FuturisticDashboard
                resumeAnalysis={resumeAnalysis}
                persona={persona}
                sessionId={sessionId}
                onStartChat={handleStartChat}
                onBack={handleBack}
              />
            </motion.div>
          )}

          {currentStep === 'chat' && sessionId && persona && (
            <motion.div
              key="chat"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              <FuturisticChat
                sessionId={sessionId}
                persona={persona}
                onBack={handleBack}
                onNext={handleNext}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default App;