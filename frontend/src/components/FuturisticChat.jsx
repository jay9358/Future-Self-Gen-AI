import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardHeader, CardBody, Button, Badge, StatusBadge } from './ui';
import ChatBox from './ui/ChatBox';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

const FuturisticChat = ({ sessionId, persona, onBack, onNext }) => {
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const [showQuickQuestions, setShowQuickQuestions] = useState(true);
  
  const socketRef = useRef(null);
  const chatContainerRef = useRef(null);

  // Initialize Socket.IO connection
  const initializeSocket = useCallback(() => {
    try {
      import('socket.io-client').then(({ io }) => {
        socketRef.current = io('http://localhost:5000', {
          transports: ['websocket', 'polling'],
          reconnection: true,
          reconnectionAttempts: 5,
          reconnectionDelay: 1000,
        });
  
        socketRef.current.on('connect', () => {
          console.log('Connected to backend');
          setIsConnected(true);
          setConnectionStatus('connected');
          setError(null);
          
          if (sessionId) {
            socketRef.current.emit('join_session', { session_id: sessionId });
          }
        });

        socketRef.current.on('disconnect', () => {
          setIsConnected(false);
          setConnectionStatus('ready');
        });

        socketRef.current.on('connect_error', (error) => {
          console.error('Connection error:', error);
          setIsConnected(false);
          setConnectionStatus('ready');
        });

        socketRef.current.on('ai_response', (data) => {
          setIsTyping(false);
          
          const aiMessage = {
            role: 'assistant',
            content: data.response,
            timestamp: Date.now()
          };
          setMessages(prev => [...prev, aiMessage]);
          setError(null);
        });

        socketRef.current.on('typing', (data) => {
          setIsTyping(data.status === 'start');
        });

        socketRef.current.on('error', (errorData) => {
          console.error('Socket error:', errorData);
          setError(errorData.error || 'An error occurred. Please try again.');
          setIsTyping(false);
        });
      }).catch(err => {
        console.error('Failed to load socket.io-client:', err);
        setIsConnected(false);
        setConnectionStatus('ready');
      });
    } catch (error) {
      console.error('Failed to initialize socket:', error);
      setIsConnected(false);
      setConnectionStatus('ready');
    }
  }, [sessionId]);

  // Initialize component
  useEffect(() => {
    if (!sessionId) {
      setConnectionStatus('no-session');
    } else {
      setConnectionStatus('connecting');
    }
    
    // Add personalized welcome message
    if (persona && sessionId) {
      const welcomeMessage = {
        role: 'assistant',
        content: `🌟 Welcome to the future, ${persona.name || 'Friend'}! I'm you from 10 years ahead, now a ${persona.current_role || 'successful professional'}. I've traveled through time to share everything I've learned on this incredible journey. I remember the uncertainty you feel now, the excitement, the fear - all of it. But here I am, 10 years later, and I can tell you: the journey is absolutely worth every step. What's on your mind today? What would you like to know about your future?`,
        timestamp: Date.now()
      };
      setMessages([welcomeMessage]);
      setConnectionStatus('ready');
    }

    if (sessionId) {
      initializeSocket();
    }

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, [persona, sessionId, initializeSocket]);

  // Handle message sending
  const handleSendMessage = async (message) => {
    if (!message || !message.trim()) return;

    if (!sessionId) {
      setError('Session not found. Please upload your resume first.');
      return;
    }

    // Hide quick questions after first message
    if (showQuickQuestions) {
      setShowQuickQuestions(false);
    }

    // Add user message immediately
    const userMessage = {
      role: 'user',
      content: message,
      timestamp: Date.now()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);
    setError(null);

    try {
      if (socketRef.current && socketRef.current.connected) {
        socketRef.current.emit('message', {
          message: message,
          session_id: sessionId,
          career: persona?.career_path || 'software_engineer'
        });
      } else {
        await sendViaHttp(message);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      handleSendError(error);
    }
  };

  // HTTP fallback
  const sendViaHttp = async (message) => {
    try {
      const response = await axios.post(`${API_URL}/chat`, {
        message: message,
        session_id: sessionId
      }, {
        timeout: 15000,
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.data.success && response.data.response) {
        const aiMessage = {
          role: 'assistant',
          content: response.data.response,
          timestamp: Date.now()
        };
        setMessages(prev => [...prev, aiMessage]);
        setError(null);
      } else {
        setError(response.data.error || 'Failed to get response');
      }
      setIsTyping(false);
      
    } catch (error) {
      console.error('HTTP request error:', error);
      handleSendError(error);
    }
  };

  // Error handling
  const handleSendError = (error) => {
    setIsTyping(false);
    
    if (error.code === 'ECONNABORTED') {
      setError('Request timed out. Please try again.');
    } else if (error.response?.data?.error) {
      setError(error.response.data.error);
    } else if (error.message?.includes('Network Error')) {
      setError('Connection error. Please check your internet and try again.');
    } else {
      setError('Unable to send message. Please try again.');
    }

    setTimeout(() => setError(null), 5000);
  };

  // Quick questions
  const quickQuestions = [
    "What should I focus on next?",
    "How did you overcome imposter syndrome?",
    "What skills changed everything for you?",
    "Tell me about your biggest breakthrough",
    "What would you do differently?",
    "How did you find work-life balance?",
    "What opportunities should I pursue?",
    "How did you handle failures?"
  ];

  // Status helpers
  const getDisplayStatus = () => {
    if (!sessionId) return 'offline';
    if (isConnected) return 'online';
    if (connectionStatus === 'ready') return 'online';
    return 'connecting';
  };

  const getStatusText = () => {
    if (!sessionId) return 'No Session';
    if (!persona) return 'Loading...';
    return `${persona.name || 'User'} → ${persona.current_role || 'Future Self'}`;
  };

  return (
    <div className="h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-cyan-900 flex flex-col overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-cyan-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-pink-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }} />
      </div>

      {/* Header */}
      <div className="relative z-10 flex-shrink-0 p-4 sm:p-6 pb-0">
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
        >
          <Card variant="glass" className="backdrop-blur-2xl bg-gradient-to-r from-slate-800/30 to-purple-800/20 border border-cyan-500/20 shadow-2xl shadow-cyan-500/10">
            <CardHeader className="p-4 sm:p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <motion.div
                    whileHover={{ scale: 1.1, rotate: 10 }}
                    className="relative"
                  >
                    <div className="w-12 h-12 sm:w-16 sm:h-16 bg-gradient-to-br from-cyan-400 via-purple-500 to-pink-500 rounded-3xl flex items-center justify-center shadow-lg shadow-purple-500/25">
                      <span className="text-2xl sm:text-3xl">🔮</span>
                    </div>
                    <motion.div 
                      className="absolute -bottom-1 -right-1 w-3 h-3 sm:w-4 sm:h-4 bg-green-400 rounded-full"
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 2, repeat: Infinity }}
                    />
                  </motion.div>
                  
                  <div>
                    <h1 className="text-xl sm:text-3xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                      Future Self Chat
                    </h1>
                    <div className="flex items-center gap-2 mt-1">
                      <StatusBadge status={getDisplayStatus()} size="sm" />
                      <span className="text-sm text-white/70">{getStatusText()}</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-3">
                  <Badge variant="primary" size="md" className="hidden sm:flex">
                    <span className="animate-pulse">AI Powered</span>
                  </Badge>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={onBack}
                    className="hover:bg-white/10 text-sm"
                  >
                    ← Back
                  </Button>
                </div>
              </div>
            </CardHeader>
          </Card>
        </motion.div>
      </div>

      {/* Error Alert */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, x: 300, scale: 0.8 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 300, scale: 0.8 }}
            className="absolute top-24 right-4 z-50 max-w-sm"
          >
            <div className="bg-red-500/10 backdrop-blur-xl border border-red-500/20 rounded-2xl p-4 flex items-start gap-3 shadow-lg">
              <span className="text-red-400 text-lg">⚠️</span>
              <div className="flex-1">
                <p className="text-red-400 text-sm">{error}</p>
              </div>
              <button 
                onClick={() => setError(null)}
                className="text-red-400 hover:text-red-300 transition-colors"
              >
                ✕
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Chat Area */}
      <div className="relative z-10 flex-1 px-4 sm:px-6 py-4 min-h-0 flex flex-col gap-4 overflow-hidden">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="flex-1 min-h-0 flex flex-col"
          ref={chatContainerRef}
        >
          <Card 
            variant="glass" 
            className="flex-1 backdrop-blur-2xl bg-gradient-to-br from-slate-800/20 to-purple-800/10 border border-cyan-500/20 overflow-hidden flex flex-col shadow-2xl shadow-cyan-500/10"
          >
            <CardBody className="p-0 flex-1 flex flex-col min-h-0">
              {/* Quick Questions */}
              <AnimatePresence>
                {showQuickQuestions && messages.length <= 1 && (
                  <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="p-4 sm:p-6 border-b border-gradient-to-r from-cyan-500/20 to-purple-500/20 bg-gradient-to-r from-purple-500/10 to-cyan-500/10"
                  >
                    <p className="text-center text-white/60 text-sm mb-4">
                      💫 Quick conversation starters
                    </p>
                    <div className="flex flex-wrap justify-center gap-2 sm:gap-3">
                      {quickQuestions.map((question, index) => (
                        <motion.button
                          key={index}
                          whileHover={{ scale: 1.05, y: -2 }}
                          whileTap={{ scale: 0.95 }}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.05 }}
                          onClick={() => handleSendMessage(question)}
                          disabled={isTyping || !sessionId}
                          className="px-3 sm:px-4 py-2 sm:py-2.5 bg-gradient-to-r from-slate-700/50 to-purple-700/50 hover:from-cyan-600/50 hover:to-purple-600/50 text-white/80 hover:text-white rounded-2xl text-xs sm:text-sm transition-all duration-300 border border-white/20 hover:border-cyan-400/50 disabled:opacity-50 disabled:cursor-not-allowed backdrop-blur-sm shadow-lg hover:shadow-xl"
                        >
                          {question}
                        </motion.button>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
              
              {/* Chat Messages Area */}
              <div className="flex-1 min-h-0 relative">
                <ChatBox
                  messages={messages}
                  onSendMessage={handleSendMessage}
                  placeholder={
                    !sessionId 
                      ? "Please upload your resume first to start chatting..."
                      : "Ask your future self anything..."
                  }
                  disabled={!sessionId}
                  isTyping={isTyping}
                  className="absolute inset-0"
                />
              </div>
            </CardBody>
          </Card>
        </motion.div>
      </div>

      {/* Bottom Navigation */}
      <div className="relative z-10 flex-shrink-0 p-4 sm:p-6 pt-0">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="flex justify-between items-center gap-4"
        >
          <Button 
            variant="secondary" 
            onClick={onBack}
            size="sm"
            className="hover:scale-105 transition-transform text-sm"
          >
            ← Back
          </Button>
          
          <div className="hidden sm:flex items-center gap-2 text-white/50 text-sm">
            <motion.div 
              className="w-2 h-2 bg-green-400 rounded-full"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
            <span>Your future self is ready to chat</span>
          </div>
          
          <Button 
            onClick={onNext}
            size="sm"
            className="hover:scale-105 transition-transform bg-gradient-to-r from-cyan-500 to-purple-500 text-sm"
          >
            Continue →
          </Button>
        </motion.div>
      </div>
    </div>
  );
};

export default FuturisticChat;