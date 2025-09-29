import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Doughnut, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import PerformanceDashboard from './PerformanceDashboard';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const API_URL = 'http://localhost:5000/api';

const FutureSelfInterface = ({ 
  sessionId, 
  selectedCareer, 
  uploadedPhotoUrl, 
  resumeData, 
  socket, 
  onBack, 
  onStartOver 
}) => {
  const [activeTab, setActiveTab] = useState('chat');
  const [messages, setMessages] = useState([]);
  const [messageInput, setMessageInput] = useState('');
  const [futureAvatar, setFutureAvatar] = useState(uploadedPhotoUrl);
  const [isLoading, setIsLoading] = useState(true);
  const [conversationId, setConversationId] = useState(null);
  const [skillsData, setSkillsData] = useState(null);
  const [projects, setProjects] = useState([]);
  const [interviewData, setInterviewData] = useState(null);
  const [salaryData, setSalaryData] = useState(null);
  const [timelineData, setTimelineData] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const [messageHistory, setMessageHistory] = useState([]);
  const [chatMode, setChatMode] = useState('normal'); // normal, professional, casual
  const [aiPersonality, setAiPersonality] = useState('encouraging');
  const [messageCount, setMessageCount] = useState(0);
  const [lastActivity, setLastActivity] = useState(new Date());
  const [showPerformanceDashboard, setShowPerformanceDashboard] = useState(false);

  useEffect(() => {
    generateFutureSelf();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (socket) {
      console.log('Socket connection status:', socket.connected);
      
      const handleReceiveMessage = (data) => {
        console.log('Received message from socket:', data);
        // Clear timeouts when response is received
        if (window.currentTimeoutId) {
          clearTimeout(window.currentTimeoutId);
          window.currentTimeoutId = null;
          console.log('Main timeout cleared successfully');
        }
        if (window.checkTimeoutId) {
          clearTimeout(window.checkTimeoutId);
          window.checkTimeoutId = null;
          console.log('Check timeout cleared successfully');
        }
        addMessage(data.message, 'future-self');
        setIsTyping(false);
      };
      
      const handleTyping = (data) => {
        console.log('Typing status:', data.status);
        setIsTyping(data.status === 'start');
      };
      
      const handleError = (data) => {
        console.error('Socket error:', data);
        // Clear timeout on error too
        if (window.currentTimeoutId) {
          clearTimeout(window.currentTimeoutId);
          window.currentTimeoutId = null;
        }
        setIsTyping(false);
        addMessage(`Sorry, I encountered an error: ${data.error || 'Unknown error'}. Please try again.`, 'future-self');
      };
      
      const handleConnect = () => {
        console.log('Socket connected in FutureSelfInterface');
      };
      
      const handleDisconnect = () => {
        console.log('Socket disconnected in FutureSelfInterface');
        // Clear timeout on disconnect
        if (window.currentTimeoutId) {
          clearTimeout(window.currentTimeoutId);
          window.currentTimeoutId = null;
        }
        setIsTyping(false);
      };
      
      // Remove all existing listeners first
      socket.off('receive_message');
      socket.off('typing');
      socket.off('error');
      socket.off('connect');
      socket.off('disconnect');
      
      // Add new listeners
      socket.on('receive_message', handleReceiveMessage);
      socket.on('typing', handleTyping);
      socket.on('error', handleError);
      socket.on('connect', handleConnect);
      socket.on('disconnect', handleDisconnect);
      
      console.log('Socket event listeners registered');
      
      // Cleanup function
      return () => {
        console.log('Cleaning up socket listeners');
        socket.off('receive_message', handleReceiveMessage);
        socket.off('typing', handleTyping);
        socket.off('error', handleError);
        socket.off('connect', handleConnect);
        socket.off('disconnect', handleDisconnect);
      };
    } else {
      console.log('No socket available in FutureSelfInterface');
    }
  }, [socket]);

  const generateFutureSelf = async () => {
    try {
      // Age the photo
      if (uploadedPhotoUrl) {
        const ageResponse = await axios.post(`${API_URL}/age-photo`, {
          session_id: sessionId,
          career: selectedCareer,
          original_photo_url: uploadedPhotoUrl
        });
        
        if (ageResponse.data.success) {
          setFutureAvatar(`http://localhost:5000${ageResponse.data.aged_photo_url}`);
        }
      }
      
      // Start conversation
      const convResponse = await axios.post(`${API_URL}/start-conversation`, {
        session_id: sessionId,
        career: selectedCareer,
        name: 'Friend'
      });
      
      if (convResponse.data.success) {
        console.log('Conversation started successfully:', convResponse.data);
        setConversationId(convResponse.data.conversation_id);
        addMessage(convResponse.data.greeting, 'future-self');
      } else {
        console.error('Failed to start conversation:', convResponse.data);
      }
      
      setIsLoading(false);
    } catch (error) {
      console.error('Generation error:', error);
      setFutureAvatar(uploadedPhotoUrl || '/default-avatar.png');
      addMessage(`Hello! I'm you from 10 years in the future as a ${selectedCareer.replace('_', ' ')}. Ask me anything!`, 'future-self');
      setIsLoading(false);
    }
  };

  const addMessage = (message, sender) => {
    console.log(`Adding message: ${sender} - ${message}`);
    const newMessage = { 
      message, 
      sender, 
      id: Date.now(),
      timestamp: new Date().toISOString(),
      chatMode,
      aiPersonality
    };
    
    setMessages(prev => {
      const newMessages = [...prev, newMessage];
      console.log('Updated messages:', newMessages);
      return newMessages;
    });
    
    // Update message history
    setMessageHistory(prev => [...prev, newMessage]);
    setMessageCount(prev => prev + 1);
    setLastActivity(new Date());
  };

  const sendMessage = () => {
    if (!messageInput.trim()) return;
    
    console.log('Sending message:', messageInput);
    console.log('Socket status:', socket ? socket.connected : 'No socket');
    console.log('Session ID:', sessionId);
    console.log('Conversation ID:', conversationId);
    console.log('Career:', selectedCareer);
    
    addMessage(messageInput, 'user');
    
    if (socket && socket.connected) {
      console.log('Emitting message via socket');
      setIsTyping(true);
      
      // Set up timeout for response (increased to 20 seconds for reliability)
      const timeoutId = setTimeout(() => {
        console.log('Response timeout - no response received within 20 seconds');
        console.log('Socket connected:', socket.connected);
        console.log('Socket ID:', socket.id);
        setIsTyping(false);
        addMessage("I'm taking longer than usual to respond. This might be due to high server load. Please try asking me something else or wait a moment.", 'future-self');
      }, 20000); // 20 second timeout for reliability
      
      // Store timeout ID globally to clear it when response is received
      window.currentTimeoutId = timeoutId;
      
      // Also set up a shorter timeout to check if we're getting any response
      const checkTimeout = setTimeout(() => {
        if (window.currentTimeoutId) {
          console.log('Warning: Still waiting for response after 5 seconds');
          console.log('Socket status:', socket.connected);
        }
      }, 5000);
      
      // Clear the check timeout when response is received
      window.checkTimeoutId = checkTimeout;
      
      console.log('Sending message data:', {
        session_id: sessionId,
        conversation_id: conversationId,
        message: messageInput,
        career: selectedCareer,
        chat_mode: chatMode,
        ai_personality: aiPersonality
      });
      
      socket.emit('message', {
        session_id: sessionId,
        message: messageInput,
        conversation_id: conversationId,
        career: selectedCareer,
        chat_mode: chatMode,
        ai_personality: aiPersonality
         });
    } else {
      console.log('Socket not connected, using fallback response');
      setIsTyping(true);
      // Fallback: simulate AI response
      setTimeout(() => {
        const responses = [
          "That's a great question! The journey has been challenging but rewarding. I've learned so much about technology and grown both personally and professionally.",
          "I remember asking myself that same question 10 years ago. The path wasn't always clear, but persistence paid off.",
          "Looking back, I can see how each decision led me to where I am today. What specific aspect interests you most?",
          "The industry has changed so much since I started. Let me share what I've learned along the way."
        ];
        const randomResponse = responses[Math.floor(Math.random() * responses.length)];
        addMessage(randomResponse, 'future-self');
        setIsTyping(false);
      }, 1000 + Math.random() * 2000); // Random delay for realism
    }
    
    setMessageInput('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setMessageHistory([]);
    setMessageCount(0);
  };

  const exportChat = () => {
    const chatData = {
      sessionId,
      career: selectedCareer,
      messages: messageHistory,
      exportedAt: new Date().toISOString(),
      messageCount,
      chatMode,
      aiPersonality
    };
    
    const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `future-self-chat-${sessionId}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const loadSkillsAnalysis = async () => {
    try {
      const response = await axios.post(`${API_URL}/skills-analysis`, {
        session_id: sessionId,
        career: selectedCareer
      });
      
      if (response.data.success) {
        setSkillsData(response.data);
      }
    } catch (error) {
      console.error('Skills analysis error:', error);
    }
  };

  const loadProjects = async () => {
    try {
      const response = await axios.post(`${API_URL}/generate-projects`, {
        career: selectedCareer,
        skill_level: 'intermediate'
      });
      
      if (response.data.success) {
        setProjects(response.data.projects);
      }
    } catch (error) {
      console.error('Projects error:', error);
      setProjects([{
        title: "Portfolio Project",
        description: "Build a showcase of your skills",
        skills_learned: ["Planning", "Execution", "Presentation"],
        duration: "2-4 weeks"
      }]);
    }
  };

  const loadInterviewPrep = async () => {
    try {
      const response = await axios.post(`${API_URL}/interview-prep`, {
        career: selectedCareer,
        experience_level: 'entry'
      });
      
      if (response.data.success) {
        setInterviewData(response.data);
      }
    } catch (error) {
      console.error('Interview prep error:', error);
    }
  };

  const loadSalaryProjection = async () => {
    try {
      const response = await axios.post(`${API_URL}/salary-projection`, {
        career: selectedCareer,
        current_skills: resumeData?.extracted_info?.skills || [],
        years_experience: resumeData?.extracted_info?.years_experience || 0
      });
      
      if (response.data.success) {
        setSalaryData(response.data);
      }
    } catch (error) {
      console.error('Salary projection error:', error);
    }
  };

  const loadTimeline = async () => {
    try {
      const response = await axios.post(`${API_URL}/generate-timeline`, {
        career: selectedCareer
      });
      
      if (response.data.success) {
        setTimelineData(response.data.timeline);
      }
    } catch (error) {
      console.error('Timeline generation error:', error);
    }
  };

  const handleTabClick = (tabName) => {
    setActiveTab(tabName);
    
    if (tabName === 'skills' && !skillsData) {
      loadSkillsAnalysis();
    } else if (tabName === 'roadmap' && !timelineData) {
      loadTimeline();
    } else if (tabName === 'projects' && projects.length === 0) {
      loadProjects();
    } else if (tabName === 'interview' && !interviewData) {
      loadInterviewPrep();
    } else if (tabName === 'salary' && !salaryData) {
      loadSalaryProjection();
    }
  };

  const getSkillsChartData = () => {
    if (!skillsData) return null;
    
    return {
      labels: ['Skills You Have', 'Skills to Learn'],
      datasets: [{
        data: [
          skillsData.match_result.matched_skills.length || 1,
          skillsData.match_result.missing_skills.length
        ],
        backgroundColor: ['#4CAF50', '#ff9800'],
        borderWidth: 0
      }]
    };
  };

  const getSalaryChartData = () => {
    if (!salaryData || !salaryData.projections) return null;
    
    const projectionEntries = Object.entries(salaryData.projections);
    
    return {
      labels: projectionEntries.map(([key, data]) => key.replace('year_', 'Year ')),
      datasets: [{
        label: 'Projected Salary',
        data: projectionEntries.map(([key, data]) => data.salary_numeric || 0),
        borderColor: '#667eea',
        backgroundColor: 'rgba(102, 126, 234, 0.1)',
        tension: 0.1,
        fill: true
      }]
    };
  };

  if (isLoading) {
    return (
      <div className="step active">
        <h2>Step 4: Meet Your Future Self</h2>
        <div className="loading active">
          <div className="spinner"></div>
          <p>Connecting to your future self...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="step active">
      <h2>Step 4: Meet Your Future Self</h2>
      
      <div className="avatar-comparison">
        <div className="avatar-box">
          <h3>You Today</h3>
          <img src={uploadedPhotoUrl} alt="Current you" />
          <p>Age: 20</p>
        </div>
        <div className="arrow">→</div>
        <div className="avatar-box">
          <h3>You in 10 Years</h3>
          <img src={futureAvatar} alt="Future you" />
          <p>Age: 30</p>
          <p>{selectedCareer.replace('_', ' ').toUpperCase()}</p>
        </div>
      </div>

      <div className="main-interface">
        {/* Tabs */}
        <div className="tabs">
          <button 
            className={`tab-button ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => handleTabClick('chat')}
          >
            💬 Chat
          </button>
          <button 
            className={`tab-button ${activeTab === 'skills' ? 'active' : ''}`}
            onClick={() => handleTabClick('skills')}
          >
            🎯 Skills Analysis
          </button>
          <button 
            className={`tab-button ${activeTab === 'roadmap' ? 'active' : ''}`}
            onClick={() => handleTabClick('roadmap')}
          >
            🗺️ Learning Path
          </button>
          <button 
            className={`tab-button ${activeTab === 'projects' ? 'active' : ''}`}
            onClick={() => handleTabClick('projects')}
          >
            💻 Projects
          </button>
          <button 
            className={`tab-button ${activeTab === 'interview' ? 'active' : ''}`}
            onClick={() => handleTabClick('interview')}
          >
            🎤 Interview Prep
          </button>
          <button 
            className={`tab-button ${activeTab === 'salary' ? 'active' : ''}`}
            onClick={() => handleTabClick('salary')}
          >
            💰 Salary Info
          </button>
        </div>

        {/* Chat Tab */}
        {activeTab === 'chat' && (
          <div className="tab-content active">
            <div className="chat-container">
              <div className="chat-header">
                <img className="chat-avatar" src={futureAvatar} alt="Future self" />
                <div className="chat-info">
                  <h3>Your Future Self</h3>
                  <p>{selectedCareer.replace('_', ' ').toUpperCase()}</p>
                  <div className="chat-stats">
                    <span>Messages: {messageCount}</span>
                    <span>Mode: {chatMode}</span>
                  </div>
                </div>
                <div className="chat-controls">
                  <select 
                    value={chatMode} 
                    onChange={(e) => setChatMode(e.target.value)}
                    className="chat-mode-selector"
                  >
                    <option value="normal">Normal</option>
                    <option value="professional">Professional</option>
                    <option value="casual">Casual</option>
                  </select>
                  <select 
                    value={aiPersonality} 
                    onChange={(e) => setAiPersonality(e.target.value)}
                    className="personality-selector"
                  >
                    <option value="encouraging">Encouraging</option>
                    <option value="realistic">Realistic</option>
                    <option value="motivational">Motivational</option>
                  </select>
                  <button onClick={clearChat} className="btn-clear">Clear</button>
                  <button onClick={exportChat} className="btn-export">Export</button>
                  <button 
                    onClick={() => setShowPerformanceDashboard(true)} 
                    className="btn-performance"
                    title="Performance Dashboard"
                  >
                    🚀
                  </button>
                </div>
              </div>
              <div className="chat-messages">
                {messages.map((msg) => (
                  <div key={msg.id} className={`message ${msg.sender}`}>
                    <div className="message-bubble">
                      <div className="message-content">{msg.message}</div>
                      <div className="message-meta">
                        <span className="message-time">
                          {new Date(msg.timestamp).toLocaleTimeString()}
                        </span>
                        {msg.sender === 'future-self' && (
                          <span className="message-mode">{msg.chatMode}</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                {isTyping && (
                  <div className="message future-self">
                    <div className="message-bubble typing-indicator">
                      <div className="typing-dots">
                        <span>.</span><span>.</span><span>.</span>
                      </div>
                      <span className="typing-text">Your future self is typing...</span>
                    </div>
                  </div>
                )}
              </div>
              <div className="chat-input">
                <input
                  type="text"
                  value={messageInput}
                  onChange={(e) => setMessageInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask your future self anything... (Press Enter to send)"
                  className="message-input"
                />
                <button 
                  onClick={sendMessage} 
                  disabled={!messageInput.trim()}
                  className="send-button"
                >
                  Send
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Skills Tab */}
        {activeTab === 'skills' && (
          <div className="tab-content active">
            <h3>Skills Gap Analysis</h3>
            {skillsData ? (
              <div>
                <div className="skills-analysis">
                  <div className="skills-chart">
                    {getSkillsChartData() && (
                      <Doughnut data={getSkillsChartData()} options={{ responsive: true }} />
                    )}
                  </div>
                  <div>
                    <div className="match-percentage">
                      <h3>Career Match Score</h3>
                      <span>{skillsData.match_result.match_percentage}%</span>
                    </div>
                  </div>
                </div>
                <div className="skills-list">
                  <div className="have-skills">
                    <h4>✅ Your Current Skills</h4>
                    <ul>
                      {skillsData.match_result.matched_skills.map((skill, index) => (
                        <li key={index}>{skill}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="need-skills">
                    <h4>📚 Skills to Learn</h4>
                    <ul>
                      {skillsData.match_result.missing_skills.map((skill, index) => (
                        <li key={index}>{skill}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ) : (
              <div>Loading skills analysis...</div>
            )}
          </div>
        )}

        {/* Roadmap Tab */}
        {activeTab === 'roadmap' && (
          <div className="tab-content active">
            <h3>Your Learning Roadmap</h3>
            {timelineData ? (
              <div className="timeline-container">
                <div className="timeline">
                  {Object.entries(timelineData).map(([key, data], index) => (
                    <div key={key} className="timeline-item" style={{ animationDelay: `${index * 0.1}s` }}>
                      <div className="timeline-content">
                        <div className="timeline-year">Year {index + 1}</div>
                        <h4 className="timeline-title">{data.title}</h4>
                        <p className="timeline-salary">{data.salary}</p>
                        <div className="timeline-achievement">
                          <strong>Achievement:</strong> {data.key_achievement}
                        </div>
                        <div className="timeline-challenge">
                          <strong>Challenge:</strong> {data.challenge}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div>Loading timeline...</div>
            )}
          </div>
        )}

        {/* Projects Tab */}
        {activeTab === 'projects' && (
          <div className="tab-content active">
            <h3>Recommended Projects to Build Your Portfolio</h3>
            <div className="projects-grid">
              {projects.map((project, index) => (
                <div key={index} className="project-card">
                  <h4>{project.title}</h4>
                  <p>{project.description}</p>
                  <div className="project-skills">
                    {(project.skills_learned || project.skills || []).map((skill, skillIndex) => (
                      <span key={skillIndex} className="skill-tag">{skill}</span>
                    ))}
                  </div>
                  <p><strong>⏱️ Duration:</strong> {project.duration}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Interview Tab */}
        {activeTab === 'interview' && (
          <div className="tab-content active">
            <h3>Interview Preparation Guide</h3>
            {interviewData ? (
              <div className="interview-sections">
                <div className="technical-questions">
                  <h4>🔧 Technical Questions</h4>
                  <ul>
                    {(interviewData.interview_prep?.technical_questions || []).map((q, index) => (
                      <li key={index}>{q}</li>
                    ))}
                  </ul>
                </div>
                <div className="behavioral-questions">
                  <h4>💭 Common Questions</h4>
                  <ul>
                    {(interviewData.interview_prep?.common_questions || []).map((q, index) => (
                      <li key={index}>{q}</li>
                    ))}
                  </ul>
                </div>
                <div className="interview-tips">
                  <h4>💡 Pro Tips for Success</h4>
                  <ul>
                    {(interviewData.interview_prep?.tips || []).map((tip, index) => (
                      <li key={index}>{tip}</li>
                    ))}
                  </ul>
                </div>
              </div>
            ) : (
              <div>Loading interview preparation...</div>
            )}
          </div>
        )}

        {/* Salary Tab */}
        {activeTab === 'salary' && (
          <div className="tab-content active">
            <h3>Salary Projections & Negotiation Guide</h3>
            {salaryData ? (
              <div>
                <div className="salary-chart">
                  {getSalaryChartData() && (
                    <Line data={getSalaryChartData()} options={{ responsive: true }} />
                  )}
                </div>
                <div className="salary-info">
                  <div className="salary-info-card">
                    <p>Starting Salary</p>
                    <strong>{salaryData.projections?.year_0?.salary || '$50,000'}</strong>
                  </div>
                  <div className="salary-info-card">
                    <p>5-Year Projection</p>
                    <strong>{salaryData.projections?.year_5?.salary || '$75,000'}</strong>
                  </div>
                  <div className="salary-info-card">
                    <p>10-Year Projection</p>
                    <strong>{salaryData.projections?.year_9?.salary || '$100,000'}</strong>
                  </div>
                </div>
                <div className="negotiation-tips">
                  <h4>Career Growth Factors</h4>
                  <ul>
                    {salaryData.projections?.year_5?.key_factors?.map((factor, index) => (
                      <li key={index}>{factor}</li>
                    )) || ['Experience', 'Skills', 'Leadership']}
                  </ul>
                </div>
              </div>
            ) : (
              <div>Loading salary projections...</div>
            )}
          </div>
        )}
      </div>

      <div className="button-group">
        <button className="btn btn-secondary" onClick={onBack}>Choose Another Career</button>
        <button className="btn" onClick={onStartOver}>Start Over</button>
      </div>

      {/* Performance Dashboard */}
      <PerformanceDashboard 
        isVisible={showPerformanceDashboard}
        onClose={() => setShowPerformanceDashboard(false)}
      />
    </div>
  );
};

export default FutureSelfInterface;
