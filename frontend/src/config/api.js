// Centralized API configuration
// Change this to point to your local server or production server

// For local development
const API_BASE_URL = 'http://localhost:5000/api';

// For production (uncomment the line below and comment the line above)
// const API_BASE_URL = 'https://ideal-youth-production.up.railway.app/api';

// Socket.IO configuration
const SOCKET_URL = API_BASE_URL.replace('/api', '');

// Export configuration
export const API_CONFIG = {
  BASE_URL: API_BASE_URL,
  SOCKET_URL: SOCKET_URL,
  ENDPOINTS: {
    // Resume endpoints
    ANALYZE_RESUME: `${API_BASE_URL}/analyze-resume`,
    UPLOAD_PHOTO: `${API_BASE_URL}/upload`,
    AGE_PHOTO: `${API_BASE_URL}/age-photo`,
    
    // Chat endpoints
    CHAT: `${API_BASE_URL}/chat`,
    START_CONVERSATION: `${API_BASE_URL}/start-conversation`,
    
    // Analysis endpoints
    SKILLS_ANALYSIS: `${API_BASE_URL}/skills-analysis`,
    GENERATE_PROJECTS: `${API_BASE_URL}/generate-projects`,
    INTERVIEW_PREP: `${API_BASE_URL}/interview-prep`,
    SALARY_PROJECTION: `${API_BASE_URL}/salary-projection`,
    GENERATE_TIMELINE: `${API_BASE_URL}/generate-timeline`,
    
    // Performance endpoints
    PERFORMANCE: `${API_BASE_URL}/performance`,
    OPTIMIZE: `${API_BASE_URL}/optimize`,
  }
};

export default API_CONFIG;
