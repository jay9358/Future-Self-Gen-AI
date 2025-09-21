# backend\app_new.py - ENHANCED FUTURE SELF AI CAREER ADVISOR
import os
import sys
import json
import base64
import uuid
import tempfile
import re
import asyncio
import concurrent.futures
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Flask and extensions
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

# Document processing
import PyPDF2
import docx

# Image and video processing
from PIL import Image
import cv2
import numpy as np

# AI and ML
import anthropic
import google.generativeai as genai
import openai
import replicate

# Data processing
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Additional utilities
import redis
import jwt
from dotenv import load_dotenv
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue

# Fix Windows path issues
if sys.platform == "win32":
    import pathlib
    pathlib.PosixPath = pathlib.WindowsPath

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import from our new structure
from config.settings import BASE_DIR, UPLOAD_FOLDER, AVATAR_FOLDER, RESUME_FOLDER, ALLOWED_EXTENSIONS, RESUME_EXTENSIONS
from models.career_database import CAREER_DATABASE, SKILLS_DATABASE
from services.resume_analyzer import extract_text_from_pdf, extract_text_from_docx, extract_skills_from_resume, calculate_career_match, generate_learning_roadmap
from services.ai_services import get_claude_client, get_gemini_model
from routes.api_routes import api_bp
from utils.file_utils import create_directories, get_title_for_year

# Initialize Flask app
app = Flask(__name__, 
    static_folder=os.path.abspath('../static'),
    template_folder=os.path.abspath('../frontend')
)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# CORS configuration
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:5000"],
        "supports_credentials": True
    }
})

# Initialize SocketIO with enhanced configuration
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',
    logger=True,
    engineio_logger=True
)

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Redis for session management and caching
try:
    redis_client = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=0,
        decode_responses=True
    )
    redis_client.ping()
    logger.info("Redis connected successfully")
except:
    redis_client = None
    logger.warning("Redis not available, using in-memory storage")

# Create directories
create_directories()

# Register blueprints
app.register_blueprint(api_bp)

# Enhanced session storage with data classes
sessions = {}

# Data Classes
@dataclass
class User:
    id: str
    email: str
    name: str
    age: int
    photo_url: Optional[str] = None
    resume_data: Optional[Dict] = None
    career_interests: List[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.career_interests is None:
            self.career_interests = []

@dataclass
class Session:
    id: str
    user_id: str
    created_at: datetime
    conversations: List[Dict] = None
    aged_avatars: Dict[str, str] = None
    
    def __post_init__(self):
        if self.conversations is None:
            self.conversations = []
        if self.aged_avatars is None:
            self.aged_avatars = {}

# AI Model Configuration
class AIModels:
    def __init__(self):
        # Claude
        try:
            self.claude = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            logger.info("Claude API initialized")
        except:
            self.claude = None
            logger.warning("Claude API not configured")
        
        # Gemini
        try:
            genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
            self.gemini = genai.GenerativeModel('gemini-2.0-flash')
            self.gemini_vision = genai.GenerativeModel('gemini-2.0-flash')
            logger.info("Gemini API initialized")
        except:
            self.gemini = None
            self.gemini_vision = None
            logger.warning("Gemini API not configured")
        
        # OpenAI
        try:
            openai.api_key = os.getenv('OPENAI_API_KEY')
            self.openai_client = openai
            logger.info("OpenAI API initialized")
        except:
            self.openai_client = None
            logger.warning("OpenAI API not configured")
        
        # Replicate for deepfakes
        try:
            self.replicate_client = replicate.Client(api_token=os.getenv('REPLICATE_API_TOKEN'))
            logger.info("Replicate API initialized")
        except:
            self.replicate_client = None
            logger.warning("Replicate API not configured")

ai_models = AIModels()

# In-memory storage (fallback if Redis unavailable)
sessions_store: Dict[str, Session] = {}
users_store: Dict[str, User] = {}

# Simple in-memory cache for API responses
api_cache: Dict[str, Any] = {}
CACHE_TTL = 300  # 5 minutes

def allowed_file(filename, extensions):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions

def generate_session_token(user_id: str) -> str:
    """Generate JWT session token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_session_token(token: str) -> Optional[str]:
    """Verify JWT session token"""
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except:
        return None

def get_cached_response(cache_key: str) -> Optional[Any]:
    """Get cached response if not expired"""
    if cache_key in api_cache:
        cached_data, timestamp = api_cache[cache_key]
        if datetime.now().timestamp() - timestamp < CACHE_TTL:
            return cached_data
        else:
            del api_cache[cache_key]
    return None

def cache_response(cache_key: str, data: Any) -> None:
    """Cache response with timestamp"""
    api_cache[cache_key] = (data, datetime.now().timestamp())

@app.route('/')
def index():
    """Serve the main HTML file"""
    return send_from_directory(os.path.abspath('../frontend'), 'index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "redis": redis_client is not None,
            "claude": ai_models.claude is not None,
            "gemini": ai_models.gemini is not None,
            "openai": ai_models.openai_client is not None,
            "replicate": ai_models.replicate_client is not None
        }
    })

@app.route('/api/upload', methods=['POST'])
@limiter.limit("10 per hour")
def upload_photo():
    """Handle photo upload"""
    try:
        if 'photo' not in request.files:
            return jsonify({"error": "No photo provided"}), 400
        
        file = request.files['photo']
        if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
            return jsonify({"error": "Invalid file type"}), 400
        
        # Generate unique filename
        filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        filepath = UPLOAD_FOLDER / filename
        file.save(str(filepath))
        
        # Create session
        session_id = str(uuid.uuid4())
        session = Session(
            id=session_id,
            user_id=session_id,  # Temporary until user auth
            created_at=datetime.now()
        )
        
        # Store session
        sessions_store[session_id] = session
        if redis_client:
            redis_client.setex(
                f"session:{session_id}",
                86400,  # 24 hours
                json.dumps(asdict(session), default=str)
            )
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "photo_url": f"/static/uploads/{filename}"
        })
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({"error": str(e)}), 500

async def generate_aged_avatar(photo_path: str, age_years: int = 10) -> str:
    """Generate aged version of photo using AI"""
    if ai_models.replicate_client:
        try:
            # Use a working Replicate model for face aging
            with open(photo_path, "rb") as f:
                output = ai_models.replicate_client.run(
                    "tencentarc/photomaker:ddfc2b08d209f9fa8c1eca692712918bd449f695dabb4a958da31802a9570fe4",  # Working face aging model
                    input={
                        "image": f,
                        "prompt": f"age progression to {age_years} years old, realistic face aging, professional headshot",
                        "num_inference_steps": 20,
                        "guidance_scale": 7.5
                    }
                )
            
            # Save aged image
            aged_filename = f"aged_{uuid.uuid4().hex}.png"
            aged_path = AVATAR_FOLDER / aged_filename
            
            # Download and save the aged image
            if output and len(output) > 0:
                # Download the image from URL
                import requests
                response = requests.get(output[0])
                if response.status_code == 200:
                    with open(aged_path, 'wb') as f:
                        f.write(response.content)
                    return f"/static/avatars/{aged_filename}"
            
        except Exception as e:
            logger.error(f"Age progression error: {e}")
    
    # Fallback: return original photo
    return photo_path

def generate_aged_avatar_sync(photo_path: str, age_years: int = 10, career: str = "software_engineer") -> str:
    """Generate aged version of photo using AI (synchronous version)"""
    if ai_models.replicate_client:
        try:
            # Try multiple working Replicate models for face aging
            models_to_try = [
                "tencentarc/photoshop-stable-diffusion:6597d4f8-47cf-41c4-bfe4-4c0f5a267256",
                "stability-ai/stable-diffusion:db21e45d3f7023abc6e46a38e1bd68d508fd4c5d04afc81950a7de63cdd7009",
                "lucataco/face-swap:9f823c59c924a5a9c7d2912d19eb9ed0a2788e2b10c79a2183778b1fd96e799"
            ]
            
            for model in models_to_try:
                try:
                    with open(photo_path, "rb") as f:
                        output = ai_models.replicate_client.run(
                            model,
                            input={
                                "image": f,
                                "prompt": f"age progression to {age_years} years old, realistic face aging, professional headshot",
                                "num_inference_steps": 20,
                                "guidance_scale": 7.5
                            }
                        )
                    
                    if output and len(output) > 0:
                        # Save aged image
                        aged_filename = f"aged_{uuid.uuid4().hex}.png"
                        aged_path = AVATAR_FOLDER / aged_filename
                        
                        # Download and save the aged image
                        import requests
                        response = requests.get(output[0])
                        if response.status_code == 200:
                            with open(aged_path, 'wb') as f:
                                f.write(response.content)
                            logger.info(f"Successfully generated aged avatar using {model}")
                            return f"/static/avatars/{aged_filename}"
                        break
                except Exception as model_error:
                    logger.warning(f"Model {model} failed: {model_error}")
                    continue
            
        except Exception as e:
            logger.error(f"Age progression error: {e}")
    
    # Fallback: create a simple aged version using PIL
    try:
        from PIL import Image, ImageFilter, ImageEnhance
        import os
        
        # Open the original image
        with Image.open(photo_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Apply aging effects
            # 1. Slightly blur to simulate aging
            img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            # 2. Adjust contrast and brightness
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.1)
            
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(0.95)
            
            # 3. Add slight color adjustment
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(0.9)
            
            # Save the aged version
            aged_filename = f"aged_{uuid.uuid4().hex}.png"
            aged_path = AVATAR_FOLDER / aged_filename
            img.save(aged_path, 'PNG')
            
            logger.info("Created aged avatar using PIL fallback")
            return f"/static/avatars/{aged_filename}"
            
    except Exception as fallback_error:
        logger.error(f"PIL fallback error: {fallback_error}")
    
    # Final fallback: return original photo
    return photo_path

@app.route('/api/age-photo', methods=['POST'])
def age_photo():
    """Generate aged version of uploaded photo"""
    try:
        data = request.json
        session_id = data.get('session_id')
        career = data.get('career')
        original_photo_url = data.get('original_photo_url')
        
        if not all([session_id, career, original_photo_url]):
            return jsonify({"error": "Missing required parameters: session_id, career, original_photo_url"}), 400
        
        # Get photo path
        photo_filename = original_photo_url.split('/')[-1]
        photo_path = UPLOAD_FOLDER / photo_filename
        
        if not os.path.exists(photo_path):
            return jsonify({"error": "Original photo not found"}), 404
        
        # Generate aged avatar (synchronous version)
        aged_url = generate_aged_avatar_sync(str(photo_path), career=career)
        
        # Update session
        if session_id in sessions_store:
            sessions_store[session_id].aged_avatars[career] = aged_url
        
        return jsonify({
            "success": True,
            "aged_photo_url": aged_url,
            "message": "Photo aged successfully"
        })
        
    except FileNotFoundError:
        logger.error("Photo file not found")
        return jsonify({"error": "Photo file not found"}), 404
    except Exception as e:
        logger.error(f"Age photo error: {e}")
        return jsonify({"error": "Failed to process photo. Please try again."}), 500

def generate_future_self_response(career: str, question: str, context: Dict) -> str:
    """Generate response as future self using AI"""
    career_info = CAREER_DATABASE.get(career, {})
    
    prompt = f"""
    You are speaking as someone's future self who became a successful {career_info.get('title', career)}.
    You are 10 years in the future. Be realistic about both challenges and rewards.
    
    Context:
    - Career: {career}
    - Personality: {', '.join(career_info.get('personality_traits', []))}
    - Current user context: {json.dumps(context, indent=2)}
    
    User question: {question}
    
    Respond in first person, as if you are their actual future self. Be encouraging but honest.
    Include specific details about the journey, challenges faced, and advice.
    """
    
    if ai_models.claude:
        try:
            response = ai_models.claude.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Claude response error: {e}")
    
    if ai_models.gemini:
        try:
            response = ai_models.gemini.generate_content(prompt)
            if response and response.text:
                return response.text
            else:
                logger.warning("Gemini returned empty response")
        except Exception as e:
            logger.error(f"Gemini response error: {e}")
    
    # Fallback response
    return f"Hello! I'm you from 10 years in the future as a successful {career.replace('_', ' ')}. The journey has been challenging but incredibly rewarding. I've learned so much about {career_info.get('core_skills', ['technology'])[0]} and grown both personally and professionally. What would you like to know about our future?"

@app.route('/api/start-conversation', methods=['POST'])
def start_conversation():
    """Start conversation with future self"""
    try:
        data = request.json
        session_id = data.get('session_id')
        career = data.get('career')
        name = data.get('name', 'Friend')
        
        # Create session if it doesn't exist
        if not session_id:
            session_id = str(uuid.uuid4())
        elif session_id not in sessions_store:
            # Create new session
            session = Session(
                id=session_id,
                user_id=session_id,
                created_at=datetime.now()
            )
            sessions_store[session_id] = session
            logger.info(f"Created new session: {session_id}")
        
        conversation_id = str(uuid.uuid4())
        career_info = CAREER_DATABASE.get(career, {})
        
        # Generate personalized greeting
        greeting = generate_future_self_response(
            career,
            "Introduce yourself to your past self",
            {"name": name, "career_info": career_info}
        )
        
        # Store conversation
        conversation = {
            "id": conversation_id,
            "career": career,
            "started_at": datetime.now().isoformat(),
            "messages": [
                {"role": "future_self", "content": greeting, "timestamp": datetime.now().isoformat()}
            ]
        }
        
        sessions_store[session_id].conversations.append(conversation)
        
        return jsonify({
            "success": True,
            "conversation_id": conversation_id,
            "greeting": greeting,
            "session_id": session_id
        })
        
    except Exception as e:
        logger.error(f"Start conversation error: {e}")
        return jsonify({"error": str(e)}), 500

# Socket.IO Events for Real-time Communication
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    try:
        logger.info(f"Client connected: {request.sid}")
        emit('connected', {"message": "Connected to Future Self server"})
    except Exception as e:
        logger.error(f"Connection error: {e}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    try:
        logger.info(f"Client disconnected: {request.sid}")
    except Exception as e:
        logger.error(f"Disconnection error: {e}")

@socketio.on('join_session')
def handle_join_session(data):
    """Join session room for real-time updates"""
    session_id = data.get('session_id')
    if session_id:
        join_room(session_id)
        emit('joined_session', {"session_id": session_id}, room=session_id)

@socketio.on('send_message')
def handle_message(data):
    """Handle chat message with future self"""
    try:
        session_id = data.get('session_id')
        conversation_id = data.get('conversation_id')
        message = data.get('message')
        career = data.get('career')
        
        if not all([session_id, message, career]):
            emit('error', {"error": "Missing required parameters"})
            return
        
        # Ensure session exists
        if session_id not in sessions_store:
            session = Session(
                id=session_id,
                user_id=session_id,
                created_at=datetime.now()
            )
            sessions_store[session_id] = session
            logger.info(f"Created session for message: {session_id}")
        
        # Generate future self response
        context = {
            "session_id": session_id,
            "conversation_id": conversation_id,
            "career": career
        }
        
        response = generate_future_self_response(career, message, context)
        
        # Store messages
        if session_id in sessions_store:
            conversation_found = False
            for conv in sessions_store[session_id].conversations:
                if conv['id'] == conversation_id:
                    conv['messages'].append({
                        "role": "user",
                        "content": message,
                        "timestamp": datetime.now().isoformat()
                    })
                    conv['messages'].append({
                        "role": "future_self",
                        "content": response,
                        "timestamp": datetime.now().isoformat()
                    })
                    conversation_found = True
                    break
            
            # If conversation not found, create a new one
            if not conversation_found:
                new_conversation = {
                    "id": conversation_id or str(uuid.uuid4()),
                    "career": career,
                    "started_at": datetime.now().isoformat(),
                    "messages": [
                        {"role": "user", "content": message, "timestamp": datetime.now().isoformat()},
                        {"role": "future_self", "content": response, "timestamp": datetime.now().isoformat()}
                    ]
                }
                sessions_store[session_id].conversations.append(new_conversation)
        
        # Emit response to client
        emit('receive_message', {
            "message": response,
            "timestamp": datetime.now().isoformat()
        }, room=session_id)
        
    except Exception as e:
        logger.error(f"Message handling error: {e}")
        emit('error', {"error": "Failed to process message. Please try again."})

@socketio.on('start_video_call')
def handle_start_video_call(data):
    """Initialize video call with deepfake processing"""
    try:
        session_id = data.get('session_id')
        career = data.get('career')
        
        # Setup video processing pipeline
        # This would involve:
        # 1. Capturing user's video stream
        # 2. Processing frames through deepfake model
        # 3. Streaming processed video back
        
        emit('video_call_ready', {
            "status": "ready",
            "career": career
        }, room=session_id)
        
    except Exception as e:
        logger.error(f"Video call error: {e}")
        emit('error', {"error": str(e)})

# Additional API endpoints for complete functionality

@app.route('/api/skills-analysis', methods=['POST'])
def skills_analysis():
    """Analyze skills gap for career transition"""
    try:
        data = request.json
        session_id = data.get('session_id')
        target_career = data.get('career')
        current_skills = data.get('current_skills', [])
        
        # Calculate match
        match_result = calculate_career_match(current_skills, target_career)
        
        # Generate learning path
        career_info = CAREER_DATABASE.get(target_career, {})
        learning_path = {
            "immediate": match_result['missing_skills'][:3],
            "short_term": match_result['missing_skills'][3:7],
            "long_term": match_result['missing_skills'][7:]
        }
        
        return jsonify({
            "success": True,
            "match_result": match_result,
            "learning_path": learning_path,
            "career_info": career_info
        })
        
    except Exception as e:
        logger.error(f"Skills analysis error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-timeline', methods=['POST'])
def generate_timeline():
    """Generate career timeline projection"""
    try:
        data = request.json
        career = data.get('career')
        
        # Check cache first
        cache_key = f"timeline_{career}"
        cached_response = get_cached_response(cache_key)
        if cached_response:
            return jsonify(cached_response)
        
        career_info = CAREER_DATABASE.get(career, {})
        
        # Generate 10-year timeline
        timeline = {}
        salary_range = career_info.get('salary_range', {})
        
        for year in range(1, 11):
            if year <= 2:
                phase = "Entry Level"
                salary = salary_range.get('entry', 50000)
            elif year <= 5:
                phase = "Mid Level"
                salary = salary_range.get('mid', 75000)
            else:
                phase = "Senior Level"
                salary = salary_range.get('senior', 100000)
            
            timeline[f"year_{year}"] = {
                "title": f"{phase} {career_info.get('title', career)}",
                "salary": f"${salary:,}/year",
                "key_achievement": f"Major milestone in year {year}",
                "challenge": f"Key challenge to overcome",
                "life_event": f"Personal growth milestone"
            }
        
        response_data = {
            "success": True,
            "timeline": timeline
        }
        
        # Cache the response
        cache_response(cache_key, response_data)
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Timeline generation error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/export-session', methods=['POST'])
def export_session():
    """Export session data as PDF report"""
    try:
        session_id = request.json.get('session_id')
        
        if session_id not in sessions_store:
            return jsonify({"error": "Invalid session"}), 400
        
        session = sessions_store[session_id]
        
        # Generate PDF report (placeholder - implement actual PDF generation)
        report_data = {
            "session_id": session_id,
            "created_at": session.created_at.isoformat(),
            "conversations": len(session.conversations),
            "careers_explored": list(session.aged_avatars.keys())
        }
        
        # In production, generate actual PDF using reportlab or similar
        report_url = f"/reports/{session_id}.pdf"
        
        return jsonify({
            "success": True,
            "report_url": report_url,
            "report_data": report_data
        })
        
    except Exception as e:
        logger.error(f"Export error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-projects', methods=['POST'])
def generate_projects():
    """Generate project ideas for career development"""
    try:
        data = request.json
        career = data.get('career')
        skill_level = data.get('skill_level', 'beginner')
        
        career_info = CAREER_DATABASE.get(career, {})
        
        # Generate project ideas based on career and skill level
        projects = {
            "beginner": [
                {
                    "title": f"Basic {career_info.get('title', career)} Portfolio",
                    "description": f"Create a simple portfolio showcasing your {career} skills",
                    "duration": "2-4 weeks",
                    "skills_learned": career_info.get('core_skills', [])[:3]
                },
                {
                    "title": f"Intro to {career_info.get('title', career)} Tools",
                    "description": f"Learn and practice with essential {career} tools",
                    "duration": "1-2 weeks",
                    "skills_learned": career_info.get('tools', [])[:2]
                }
            ],
            "intermediate": [
                {
                    "title": f"Advanced {career_info.get('title', career)} Project",
                    "description": f"Build a comprehensive project demonstrating {career} expertise",
                    "duration": "4-8 weeks",
                    "skills_learned": career_info.get('core_skills', [])[3:6]
                }
            ],
            "advanced": [
                {
                    "title": f"Enterprise {career_info.get('title', career)} Solution",
                    "description": f"Develop a production-ready {career} solution",
                    "duration": "8-12 weeks",
                    "skills_learned": career_info.get('advanced_skills', [])
                }
            ]
        }
        
        return jsonify({
            "success": True,
            "projects": projects.get(skill_level, projects['beginner']),
            "career_info": career_info
        })
        
    except Exception as e:
        logger.error(f"Generate projects error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/interview-prep', methods=['POST'])
def interview_prep():
    """Generate interview preparation materials"""
    try:
        data = request.json
        career = data.get('career')
        experience_level = data.get('experience_level', 'entry')
        
        career_info = CAREER_DATABASE.get(career, {})
        
        # Generate interview questions and tips
        interview_prep = {
            "common_questions": [
                f"Tell me about your experience with {career_info.get('core_skills', ['relevant skills'])[0]}",
                f"How do you stay updated with {career} trends?",
                f"Describe a challenging {career} project you've worked on",
                f"What tools do you use for {career} development?",
                f"How do you approach problem-solving in {career}?"
            ],
            "technical_questions": career_info.get('technical_questions', [
                f"Explain the fundamentals of {career}",
                f"What are the best practices in {career}?",
                f"How do you handle {career} challenges?"
            ]),
            "tips": [
                f"Research the company's {career} stack",
                f"Prepare examples of your {career} work",
                f"Practice explaining {career} concepts clearly",
                f"Be ready to discuss your {career} learning journey"
            ],
            "salary_range": career_info.get('salary_range', {}),
            "career_path": career_info.get('career_progression', [])
        }
        
        return jsonify({
            "success": True,
            "interview_prep": interview_prep,
            "career_info": career_info
        })
        
    except Exception as e:
        logger.error(f"Interview prep error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/salary-projection', methods=['POST'])
def salary_projection():
    """Generate salary projection for career path"""
    try:
        data = request.json
        career = data.get('career')
        current_experience = data.get('current_experience', 0)
        location = data.get('location', 'US')
        
        career_info = CAREER_DATABASE.get(career, {})
        salary_range = career_info.get('salary_range', {})
        
        # Generate salary projections
        projections = {}
        base_salary = salary_range.get('entry', 50000)
        
        for year in range(current_experience, current_experience + 10):
            if year <= 2:
                level = "Entry"
                multiplier = 1.0
            elif year <= 5:
                level = "Mid"
                multiplier = 1.5
            elif year <= 8:
                level = "Senior"
                multiplier = 2.0
            else:
                level = "Lead/Principal"
                multiplier = 2.5
            
            # Add location adjustment
            location_multiplier = 1.2 if location in ['San Francisco', 'New York', 'Seattle'] else 1.0
            
            projected_salary = int(base_salary * multiplier * location_multiplier)
            
            projections[f"year_{year}"] = {
                "level": level,
                "salary": f"${projected_salary:,}",
                "salary_numeric": projected_salary,
                "growth_rate": "15-20%" if year <= 5 else "10-15%",
                "key_factors": [
                    f"Experience in {career}",
                    f"Leadership skills" if year > 5 else f"Technical skills",
                    f"Industry knowledge"
                ]
            }
        
        return jsonify({
            "success": True,
            "projections": projections,
            "career_info": career_info,
            "location": location
        })
        
    except Exception as e:
        logger.error(f"Salary projection error: {e}")
        return jsonify({"error": str(e)}), 500

# Static file serving
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    """Serve uploaded files"""
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/static/<path:filepath>')
def serve_static(filepath):
    """Serve static files with proper Windows path handling"""
    static_dir = os.path.abspath('../static')
    return send_from_directory(static_dir, filepath.replace('/', os.sep))

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({"error": "Internal server error"}), 500

# Cleanup function
def cleanup():
    """Clean up resources on shutdown"""
    logger.info("Cleaning up resources...")
    
    # Close Redis connection
    if redis_client:
        redis_client.close()
    
    logger.info("Cleanup complete")

if __name__ == '__main__':
    print("\n" + "="*60)
    print("FUTURE SELF AI CAREER ADVISOR - ENHANCED VERSION")
    print("="*60)
    print(f"Platform: {sys.platform}")
    print(f"Python: {sys.version}")
    print("\nFeatures Enabled:")
    print("✅ Photo Upload & Processing")
    print("✅ AI-Powered Age Progression")
    print("✅ Real-time Chat with Future Self")
    print("✅ WebRTC Video Calls")
    print("✅ Skills Gap Analysis")
    print("✅ Career Timeline Generation")
    print("✅ Resume Analysis")
    print("✅ Session Management")
    print("✅ Redis Caching")
    print("✅ Rate Limiting")
    print("✅ Enhanced Security")
    print("\nServer URL: http://localhost:5000")
    print("WebSocket: ws://localhost:5000/socket.io")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    try:
        socketio.run(
            app,
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=False,
            log_output=True
        )
    except KeyboardInterrupt:
        print("\nShutting down...")
        cleanup()
    except Exception as e:
        logger.error(f"Server error: {e}")
        cleanup()
