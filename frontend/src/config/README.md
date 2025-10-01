# API Configuration

This directory contains centralized API configuration for the Future Self application.

## Usage

The main configuration file is `api.js` which exports `API_CONFIG` object containing all API endpoints and base URLs.

### Switching Between Environments

To switch between local development and production:

1. **For Local Development** (default):
   ```javascript
   const API_BASE_URL = 'http://localhost:5000/api';
   ```

2. **For Production**:
   ```javascript
   const API_BASE_URL = 'https://ideal-youth-production.up.railway.app/api';
   ```

Simply uncomment the production line and comment the local development line in `api.js`.

### Available Endpoints

The configuration includes all API endpoints used throughout the application:

- **Resume endpoints**: `ANALYZE_RESUME`, `UPLOAD_PHOTO`, `AGE_PHOTO`
- **Chat endpoints**: `CHAT`, `START_CONVERSATION`
- **Analysis endpoints**: `SKILLS_ANALYSIS`, `GENERATE_PROJECTS`, `INTERVIEW_PREP`, `SALARY_PROJECTION`, `GENERATE_TIMELINE`
- **Performance endpoints**: `PERFORMANCE`, `OPTIMIZE`

### Usage in Components

Import and use the configuration in your components:

```javascript
import { API_CONFIG } from '../config/api';

// Use specific endpoints
const response = await axios.post(API_CONFIG.ENDPOINTS.ANALYZE_RESUME, data);

// Use base URL for custom endpoints
const response = await axios.get(`${API_CONFIG.BASE_URL}/custom-endpoint`);
```

### Socket.IO Configuration

The `SOCKET_URL` is automatically derived from the `API_BASE_URL` by removing the `/api` suffix, making it easy to maintain consistency between HTTP and WebSocket connections.
