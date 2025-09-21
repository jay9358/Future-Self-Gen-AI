import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Card, CardHeader, CardBody, CardTitle, Button, ChatBox, Badge, StatusBadge } from './ui';
import axios from 'axios';

const API_URL = 'https://striking-bravery-production.up.railway.app/api';

const FuturisticChat = ({ sessionId, persona, onBack, onNext }) => {
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState(null);
  const socketRef = useRef(null);
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const [showQuickQuestions, setShowQuickQuestions] = useState(true);

  useEffect(() => {
    // Set initial status based on sessionId
    if (!sessionId) {
      setConnectionStatus('no-session');
    } else {
      setConnectionStatus('connecting');
    }
    
    // Add personalized welcome message
    if (persona && sessionId) {
      const welcomeMessage = {
        role: 'assistant',
        content: `Hey ${persona.name || 'Friend'}! I'm you from 10 years in the future, now a ${persona.current_role || 'successful professional'}. I've been where you are now, and I want to share everything I've learned to help you succeed. I remember the uncertainty, the excitement, the fear - all of it. But here I am, 10 years later, and I can tell you: the journey is worth every step. What's on your heart today?`,
        timestamp: Date.now()
      };
      setMessages([welcomeMessage]);
      setConnectionStatus('ready');
    }

    // Initialize Socket.IO connection
    if (sessionId) {
      initializeSocket();
    }

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, [persona, sessionId]);

  const initializeSocket = () => {
    try {
      import('socket.io-client').then(({ io }) => {
        socketRef.current = io('https://striking-bravery-production.up.railway.app', {
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
  };

  const handleSendMessage = async (message) => {
    if (!message || !message.trim()) {
      return;
    }

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

    // Auto-hide error after 5 seconds
    setTimeout(() => setError(null), 5000);
  };

  const quickQuestions = [
    "What should I focus on next?",
    "How did you overcome imposter syndrome?",
    "What skills changed everything for you?",
    "Tell me about your biggest breakthrough",
    "What would you do differently?",
    "How did you find work-life balance?"
  ];

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
    <div className="h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 flex flex-col">
      {/* Fixed Header */}
      <div className="flex-shrink-0 p-4 lg:p-6 pb-0">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card variant="glass" className="backdrop-blur-xl bg-white/5 border border-white/10">
            <CardHeader className="p-4 lg:p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <motion.div
                    whileHover={{ scale: 1.05, rotate: 5 }}
                    className="relative"
                  >
                    <div className="w-14 h-14 bg-gradient-to-br from-cyan-400 via-purple-500 to-pink-500 rounded-2xl flex items-center justify-center shadow-lg shadow-purple-500/25">
                      <span className="text-2xl">🔮</span>
                    </div>
                    <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-pulse" />
                  </motion.div>
                  
                  <div>
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
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
                    size="md" 
                    onClick={onBack}
                    className="hover:bg-white/10"
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
      {error && (
        <motion.div
          initial={{ opacity: 0, x: 300 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 300 }}
          className="absolute top-24 right-4 z-50 max-w-sm"
        >
          <div className="bg-red-500/10 backdrop-blur-xl border border-red-500/20 rounded-xl p-4 flex items-start gap-3">
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

      {/* Main Chat Area */}
      <div className="flex-1 px-4 lg:px-6 py-4 min-h-0 flex flex-col gap-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="flex-1 min-h-0"
        >
          <Card 
            variant="glass" 
            className="h-full backdrop-blur-xl bg-white/5 border border-white/10 overflow-hidden"
          >
            <CardBody className="p-0 h-full flex flex-col">
              {/* Quick Questions - Shows at top when no messages */}
              {showQuickQuestions && messages.length <= 1 && (
                <motion.div
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-4 border-b border-white/10 bg-gradient-to-b from-purple-500/10 to-transparent"
                >
                  <p className="text-center text-white/60 text-sm mb-3">
                    Quick conversation starters
                  </p>
                  <div className="flex flex-wrap justify-center gap-2">
                    {quickQuestions.map((question, index) => (
                      <motion.button
                        key={index}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.05 }}
                        onClick={() => handleSendMessage(question)}
                        disabled={isTyping || !sessionId}
                        className="px-3 py-1.5 bg-white/10 hover:bg-white/20 text-white/80 hover:text-white rounded-full text-xs transition-all duration-300 border border-white/20 hover:border-white/30 disabled:opacity-50 disabled:cursor-not-allowed backdrop-blur-sm"
                      >
                        {question}
                      </motion.button>
                    ))}
                  </div>
                </motion.div>
              )}
              
              {/* Chat Messages Area */}
              <div className="flex-1 min-h-0">
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
                  className="h-full"
                />
              </div>
            </CardBody>
          </Card>
        </motion.div>
      </div>

      {/* Bottom Navigation */}
      <div className="flex-shrink-0 p-4 lg:p-6 pt-0">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="flex justify-between items-center"
        >
          <Button 
            variant="secondary" 
            onClick={onBack}
            size="lg"
            className="hover:scale-105 transition-transform"
          >
            ← Back to Dashboard
          </Button>
          
          <div className="hidden sm:flex items-center gap-2 text-white/50 text-sm">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            <span>Your future self is ready to chat</span>
          </div>
          
          <Button 
            onClick={onNext}
            size="lg"
            className="hover:scale-105 transition-transform bg-gradient-to-r from-cyan-500 to-purple-500"
          >
            Continue Journey →
          </Button>
        </motion.div>
      </div>
    </div>
  );
};

export default FuturisticChat;