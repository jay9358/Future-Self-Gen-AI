# Future Self AI - Backend

This is the Flask backend for the Future Self AI Career Time Machine application.

## Project Structure

```
backend/
├── config/
│   ├── __init__.py
│   └── settings.py
├── models/
│   ├── __init__.py
│   └── career_database.py
├── services/
│   ├── __init__.py
│   ├── resume_analyzer.py
│   └── ai_services.py
├── routes/
│   ├── __init__.py
│   └── api_routes.py
├── utils/
│   ├── __init__.py
│   └── file_utils.py
├── app.py (original)
├── app_new.py (restructured)
└── requirements.txt
```

## Features

- Modular Flask application structure
- Resume analysis and skills extraction
- AI-powered career guidance
- Real-time communication with Socket.IO
- Career matching algorithms
- Learning roadmap generation

## Getting Started

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
# Create .env file with:
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key
OPENAI_API_KEY=your_openai_key
REPLICATE_API_TOKEN=your_replicate_token
```

3. Run the application:
```bash
python app_new.py
```

## API Endpoints

- `GET /` - Serve the main HTML file
- `POST /api/upload` - Upload photo
- `POST /api/upload-resume` - Upload and analyze resume
- `POST /api/age-photo` - Age the uploaded photo
- `POST /api/start-conversation` - Start conversation with future self
- `POST /api/skills-gap-analysis` - Analyze skills gap
- `POST /api/generate-projects` - Generate project recommendations
- `POST /api/interview-prep` - Get interview preparation materials
- `POST /api/salary-projection` - Get salary projections

## Socket.IO Events

- `send_message` - Send message to future self
- `receive_message` - Receive response from future self
- `error` - Handle errors

## Architecture

The application follows a modular structure:

- **Config**: Application settings and configuration
- **Models**: Data models and database definitions
- **Services**: Business logic and external service integrations
- **Routes**: API endpoints and route handlers
- **Utils**: Utility functions and helpers
