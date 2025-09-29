import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const ChatBox = ({ 
  messages = [],
  onSendMessage,
  placeholder = "Ask your future self anything...",
  disabled = false,
  className = ''
}) => {
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isNearBottom, setIsNearBottom] = useState(true);
  const [isFocused, setIsFocused] = useState(false);
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const messagesContainerRef = useRef(null);

  // Scroll functions
  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ 
        behavior: "smooth",
        block: "end",
        inline: "nearest"
      });
    }
  };

  const scrollToBottomInstant = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ 
        behavior: "auto",
        block: "end",
        inline: "nearest"
      });
    }
  };

  // Handle scroll events
  const handleScroll = () => {
    if (messagesContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = messagesContainerRef.current;
      const isNear = scrollHeight - scrollTop - clientHeight < 100;
      setIsNearBottom(isNear);
    }
  };

  // Auto-scroll effects
  useEffect(() => {
    scrollToBottomInstant();
  }, []);

  useEffect(() => {
    if (isNearBottom) {
      const timer = setTimeout(() => {
        scrollToBottom();
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [messages, isNearBottom]);

  // Message handling
  const handleSend = async () => {
    if (!inputValue.trim() || disabled) return;
    
    const message = inputValue.trim();
    setInputValue('');
    setIsTyping(true);
    
    try {
      await onSendMessage(message);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className={`relative h-full bg-gradient-to-br from-slate-900/50 via-purple-900/20 to-cyan-900/30 backdrop-blur-2xl rounded-3xl border border-cyan-500/20 shadow-2xl shadow-cyan-500/10 ${className}`}>
      {/* Custom Scrollbar Styles */}
      <style jsx>{`
        .futuristic-scroll::-webkit-scrollbar {
          width: 8px;
        }
        .futuristic-scroll::-webkit-scrollbar-track {
          background: rgba(0, 0, 0, 0.1);
          border-radius: 4px;
        }
        .futuristic-scroll::-webkit-scrollbar-thumb {
          background: linear-gradient(180deg, #06b6d4, #8b5cf6);
          border-radius: 4px;
          border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .futuristic-scroll::-webkit-scrollbar-thumb:hover {
          background: linear-gradient(180deg, #0891b2, #7c3aed);
        }
      `}</style>

      {/* Messages Container - Absolute positioned with overflow scroll */}
      <div 
        ref={messagesContainerRef}
        onScroll={handleScroll}
        className="absolute left-0 right-0 overflow-y-auto overflow-x-hidden p-6 space-y-6 futuristic-scroll"
        style={{ 
          scrollBehavior: 'smooth',
          top: '110px',
          height: '15rem'
        }}
      >
        <AnimatePresence>
          {messages.map((message, index) => (
            <MessageBubble key={index} message={message} index={index} />
          ))}
        </AnimatePresence>
        
        {/* Typing Indicator */}
        {isTyping && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -20, scale: 0.9 }}
            className="flex items-center space-x-3 text-cyan-400/80"
          >
            <div className="flex space-x-1">
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  animate={{ 
                    scale: [1, 1.3, 1],
                    opacity: [0.5, 1, 0.5]
                  }}
                  transition={{ 
                    duration: 1.2, 
                    repeat: Infinity, 
                    delay: i * 0.2,
                    ease: "easeInOut"
                  }}
                  className="w-2 h-2 bg-gradient-to-r from-cyan-400 to-purple-500 rounded-full"
                />
              ))}
            </div>
            <span className="text-sm font-medium">Future self is thinking...</span>
          </motion.div>
        )}
        
        <div ref={messagesEndRef} />
        
        {/* Scroll to Bottom Button */}
        {!isNearBottom && (
          <motion.button
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 20 }}
            onClick={scrollToBottom}
            className="absolute right-6 z-30 p-4 bg-gradient-to-r from-cyan-500 to-purple-600 text-white rounded-2xl shadow-lg hover:shadow-xl hover:shadow-cyan-500/25 transition-all duration-300 hover:scale-110 backdrop-blur-sm border border-white/20 group"
            style={{
              top: 'calc(110px + 15rem - 80px)'
            }}
            title="Scroll to bottom"
          >
            <motion.svg 
              className="w-5 h-5" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
              animate={{ y: [0, -2, 0] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
            </motion.svg>
          </motion.button>
        )}
      </div>

      {/* Input Area - Absolute positioned at bottom */}
      <div 
        className="absolute left-0 right-0 p-6 border-t border-gradient-to-r from-cyan-500/20 to-purple-500/20 bg-gradient-to-r from-slate-900/30 to-purple-900/20 backdrop-blur-sm rounded-b-3xl"
        style={{
          top: 'calc(110px + 15rem)',
          height: 'auto'
        }}
      >
        <div className="flex space-x-4">
          <div className="flex-1 relative group">
            <motion.input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              placeholder={placeholder}
              disabled={disabled || isTyping}
              className={`w-full px-6 py-4 bg-gradient-to-r from-slate-800/50 to-purple-800/30 border-2 rounded-2xl text-white placeholder-white/50 focus:outline-none transition-all duration-300 disabled:opacity-50 backdrop-blur-sm shadow-lg ${
                isFocused 
                  ? 'border-cyan-400 shadow-cyan-400/25 shadow-lg' 
                  : 'border-white/20 hover:border-cyan-400/50'
              }`}
            />
            {isFocused && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                className="absolute inset-0 rounded-2xl bg-gradient-to-r from-cyan-500/10 to-purple-500/10 pointer-events-none"
              />
            )}
          </div>
          
          <motion.button
            whileHover={{ scale: 1.05, rotate: 5 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleSend}
            disabled={!inputValue.trim() || disabled || isTyping}
            className="px-6 py-4 bg-gradient-to-r from-cyan-500 to-purple-600 text-white rounded-2xl font-semibold hover:shadow-lg hover:shadow-cyan-500/25 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center min-w-[60px] backdrop-blur-sm border border-white/20 shadow-lg group"
          >
            <motion.div
              animate={isTyping ? { rotate: 360 } : { rotate: 0 }}
              transition={{ duration: 1, repeat: isTyping ? Infinity : 0 }}
            >
              <SendIcon />
            </motion.div>
          </motion.button>
        </div>
      </div>
    </div>
  );
};

const MessageBubble = ({ message, index }) => {
  const isUser = message.role === 'user';
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 30, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -30, scale: 0.9 }}
      transition={{ 
        duration: 0.4, 
        delay: index * 0.05,
        ease: "easeOut"
      }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div className={`max-w-[80%] sm:max-w-[70%] lg:max-w-[60%] relative`}>
        {/* Message Bubble */}
        <div className={`px-6 py-4 rounded-3xl shadow-lg backdrop-blur-sm ${
          isUser 
            ? 'bg-gradient-to-r from-cyan-500 to-purple-600 text-white rounded-br-lg shadow-cyan-500/25' 
            : 'bg-gradient-to-r from-slate-800/60 to-purple-800/40 text-white/90 border border-white/20 rounded-bl-lg shadow-white/10'
        }`}>
          <div className="text-sm leading-relaxed break-words whitespace-pre-wrap">
            {message.content}
          </div>
          <div className={`text-xs mt-3 opacity-70 ${
            isUser ? 'text-white/70' : 'text-white/50'
          }`}>
            {new Date(message.timestamp || Date.now()).toLocaleTimeString([], { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </div>
        </div>
        
        {/* Avatar */}
        <div className={`absolute -bottom-2 ${isUser ? '-right-2' : '-left-2'} w-8 h-8 rounded-full flex items-center justify-center shadow-lg ${
          isUser 
            ? 'bg-gradient-to-r from-cyan-400 to-purple-500' 
            : 'bg-gradient-to-r from-purple-500 to-pink-500'
        }`}>
          <span className="text-xs font-bold">
            {isUser ? '👤' : '🔮'}
          </span>
        </div>
      </div>
    </motion.div>
  );
};

const SendIcon = () => (
  <svg 
    className="w-5 h-5" 
    fill="none" 
    stroke="currentColor" 
    viewBox="0 0 24 24"
  >
    <path 
      strokeLinecap="round" 
      strokeLinejoin="round" 
      strokeWidth={2} 
      d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" 
    />
  </svg>
);

export default ChatBox;