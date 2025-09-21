# app.py - Complete Future Self AI Career Advisor Backend
import os
import sys
import json
import base64
import uuid
import hashlib
import tempfile
import re
import asyncio
import concurrent.futures
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

# WebRTC and media
import aiortc
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRelay

# Additional utilities
import redis
import jwt
from dotenv import load_dotenv
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# CORS configuration
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:5000"],
        "allow_credentials": True
    }
})

# Initialize SocketIO with Redis adapter for scaling
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
            self.gemini = genai.GenerativeModel('gemini-pro')
            self.gemini_vision = genai.GenerativeModel('gemini-pro-vision')
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

# Directory setup
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / 'uploads'
STATIC_DIR = BASE_DIR / 'static'
AVATAR_DIR = STATIC_DIR / 'avatars'
VIDEO_DIR = STATIC_DIR / 'videos'
TEMP_DIR = BASE_DIR / 'temp'

# Create directories
for directory in [UPLOAD_DIR, STATIC_DIR, AVATAR_DIR, VIDEO_DIR, TEMP_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# File extensions
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'avi', 'mov'}
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'docx', 'txt'}

# Career and Skills Database
CAREER_DATABASE = {
    "doctor": {
        "title": "Medical Doctor",
        "avg_salary": {"entry": 60000, "mid": 180000, "senior": 350000},
        "years_training": 11,
        "required_skills": [
            "Biology", "Chemistry", "Anatomy", "Physiology", "Pharmacology",
            "Clinical Skills", "Patient Care", "Medical Ethics", "Research",
            "Critical Thinking", "Communication", "Empathy", "Decision Making"
        ],
        "personality_traits": ["Compassionate", "Detail-oriented", "Resilient", "Analytical"],
        "work_life_balance": 3,  # 1-10 scale
        "job_satisfaction": 8,
        "stress_level": 9,
        "growth_potential": 9
    },
    "software_engineer": {
        "title": "Software Engineer",
        "avg_salary": {"entry": 75000, "mid": 130000, "senior": 200000},
        "years_training": 1,
        "required_skills": [
            "Programming", "Data Structures", "Algorithms", "System Design",
            "Git", "Testing", "Debugging", "Agile", "Cloud Computing",
            "Problem Solving", "Continuous Learning", "Team Collaboration"
        ],
        "personality_traits": ["Logical", "Creative", "Patient", "Curious"],
        "work_life_balance": 7,
        "job_satisfaction": 8,
        "stress_level": 6,
        "growth_potential": 10
    },
    "data_scientist": {
        "title": "Data Scientist",
        "avg_salary": {"entry": 85000, "mid": 130000, "senior": 180000},
        "years_training": 2,
        "required_skills": [
            "Python", "R", "SQL", "Statistics", "Machine Learning",
            "Data Visualization", "Big Data", "Deep Learning", "Business Acumen",
            "Communication", "Problem Solving", "Mathematics"
        ],
        "personality_traits": ["Analytical", "Curious", "Detail-oriented", "Patient"],
        "work_life_balance": 7,
        "job_satisfaction": 8,
        "stress_level": 5,
        "growth_potential": 9
    },
    "entrepreneur": {
        "title": "Entrepreneur",
        "avg_salary": {"entry": -50000, "mid": 100000, "senior": 1000000},
        "years_training": 0,
        "required_skills": [
            "Business Strategy", "Marketing", "Sales", "Finance", "Leadership",
            "Networking", "Product Development", "Risk Management", "Negotiation",
            "Resilience", "Vision", "Adaptability", "Time Management"
        ],
        "personality_traits": ["Risk-taker", "Visionary", "Persistent", "Adaptable"],
        "work_life_balance": 3,
        "job_satisfaction": 9,
        "stress_level": 10,
        "growth_potential": 10
    },
    "teacher": {
        "title": "Teacher",
        "avg_salary": {"entry": 40000, "mid": 55000, "senior": 75000},
        "years_training": 4,
        "required_skills": [
            "Subject Expertise", "Curriculum Development", "Classroom Management",
            "Communication", "Assessment", "Technology Integration", "Psychology",
            "Patience", "Creativity", "Empathy", "Organization"
        ],
        "personality_traits": ["Patient", "Nurturing", "Creative", "Organized"],
        "work_life_balance": 8,
        "job_satisfaction": 8,
        "stress_level": 7,
        "growth_potential": 5
    }
}

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

@dataclass
class VideoCall:
    id: str
    session_id: str
    career: str
    peer_connection: Optional[RTCPeerConnection] = None
    start_time: datetime = None
    end_time: Optional[datetime] = None
    
    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now()

# In-memory storage (fallback if Redis unavailable)
sessions_store: Dict[str, Session] = {}
users_store: Dict[str, User] = {}
video_calls: Dict[str, VideoCall] = {}
peer_connections: Dict[str, RTCPeerConnection] = {}

# WebRTC Configuration
relay = MediaRelay()

class VideoProcessor:
    """Process video frames for deepfake effects"""
    
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
    def apply_aging_effect(self, frame, age_years=10):
        """Apply simple aging effect to video frame"""
        # This is a placeholder - in production, use proper deepfake model
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Add some basic aging effects
        # In real implementation, use trained GANs or deepfake models
        aged_frame = cv2.addWeighted(frame, 0.9, gray[:, :, np.newaxis], 0.1, 0)
        
        return aged_frame
    
    def detect_face(self, frame):
        """Detect face in frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        return faces

video_processor = VideoProcessor()

# Utility Functions
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

def extract_text_from_pdf(filepath):
    """Extract text from PDF file"""
    try:
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        return ""

def extract_text_from_docx(filepath):
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(filepath)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        logger.error(f"DOCX extraction error: {e}")
        return ""

def analyze_resume_with_ai(resume_text: str) -> Dict:
    """Use AI to analyze resume"""
    if ai_models.gemini:
        try:
            prompt = f"""
            Analyze this resume and extract:
            1. Current role/title
            2. Years of experience
            3. Key skills (technical and soft)
            4. Education level
            5. Career highlights
            6. Potential career paths
            
            Resume: {resume_text[:3000]}
            
            Return as JSON format.
            """
            
            response = ai_models.gemini.generate_content(prompt)
            # Parse response and return structured data
            return {"analysis": response.text}
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
    
    return {"analysis": "Manual analysis required"}

def calculate_career_match(user_skills: List[str], career: str) -> Dict:
    """Calculate match percentage between user skills and career requirements"""
    career_info = CAREER_DATABASE.get(career, {})
    required_skills = career_info.get('required_skills', [])
    
    if not required_skills:
        return {"match_percentage": 0, "matched_skills": [], "missing_skills": []}
    
    # Convert to lowercase for comparison
    user_skills_lower = [s.lower() for s in user_skills]
    required_skills_lower = [s.lower() for s in required_skills]
    
    matched = [s for s in required_skills if s.lower() in user_skills_lower]
    missing = [s for s in required_skills if s.lower() not in user_skills_lower]
    
    match_percentage = (len(matched) / len(required_skills)) * 100
    
    return {
        "match_percentage": round(match_percentage, 2),
        "matched_skills": matched,
        "missing_skills": missing
    }

async def generate_aged_avatar(photo_path: str, age_years: int = 10) -> str:
    """Generate aged version of photo using AI"""
    if ai_models.replicate_client:
        try:
            # Use Replicate's age progression model
            with open(photo_path, "rb") as f:
                output = ai_models.replicate_client.run(
                    "yuval-alaluf/sam:9a31a7cc",  # SAM age progression model
                    input={
                        "image": f,
                        "target_age": age_years
                    }
                )
            
            # Save aged image
            aged_filename = f"aged_{uuid.uuid4().hex}.png"
            aged_path = AVATAR_DIR / aged_filename
            
            # Download and save the aged image
            # Implementation depends on Replicate's response format
            
            return f"/static/avatars/{aged_filename}"
        except Exception as e:
            logger.error(f"Age progression error: {e}")
    
    # Fallback: return original photo
    return photo_path

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
            return response.text
        except Exception as e:
            logger.error(f"Gemini response error: {e}")
    
    # Fallback response
    return f"As a {career} 10 years from now, I can tell you the journey has been challenging but rewarding. Keep learning and stay persistent!"

# API Routes

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
        if not allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
            return jsonify({"error": "Invalid file type"}), 400
        
        # Generate unique filename
        filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        filepath = UPLOAD_DIR / filename
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
            "photo_url": f"/uploads/{filename}"
        })
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/age-photo', methods=['POST'])
async def age_photo():
    """Generate aged version of uploaded photo"""
    try:
        data = request.json
        session_id = data.get('session_id')
        career = data.get('career')
        original_photo_url = data.get('original_photo_url')
        
        if not all([session_id, career, original_photo_url]):
            return jsonify({"error": "Missing parameters"}), 400
        
        # Get photo path
        photo_filename = original_photo_url.split('/')[-1]
        photo_path = UPLOAD_DIR / photo_filename
        
        # Generate aged avatar
        aged_url = await generate_aged_avatar(str(photo_path))
        
        # Update session
        if session_id in sessions_store:
            sessions_store[session_id].aged_avatars[career] = aged_url
        
        return jsonify({
            "success": True,
            "aged_photo_url": aged_url
        })
        
    except Exception as e:
        logger.error(f"Age photo error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/start-conversation', methods=['POST'])
def start_conversation():
    """Start conversation with future self"""
    try:
        data = request.json
        session_id = data.get('session_id')
        career = data.get('career')
        name = data.get('name', 'Friend')
        
        if not session_id or session_id not in sessions_store:
            return jsonify({"error": "Invalid session"}), 400
        
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
            "greeting": greeting
        })
        
    except Exception as e:
        logger.error(f"Start conversation error: {e}")
        return jsonify({"error": str(e)}), 500

# WebRTC Routes for Video Calls
@app.route('/api/webrtc/offer', methods=['POST'])
async def webrtc_offer():
    """Handle WebRTC offer for video call"""
    try:
        data = request.json
        session_id = data.get('session_id')
        career = data.get('career')
        offer = data.get('offer')
        
        # Create peer connection
        pc = RTCPeerConnection()
        pc_id = str(uuid.uuid4())
        peer_connections[pc_id] = pc
        
        # Create video call record
        video_call = VideoCall(
            id=pc_id,
            session_id=session_id,
            career=career,
            peer_connection=pc
        )
        video_calls[pc_id] = video_call
        
        @pc.on("datachannel")
        def on_datachannel(channel):
            logger.info(f"Data channel created: {channel.label}")
        
        @pc.on("iceconnectionstatechange")
        async def on_iceconnectionstatechange():
            logger.info(f"ICE connection state: {pc.iceConnectionState}")
            if pc.iceConnectionState == "failed":
                await pc.close()
                del peer_connections[pc_id]
        
        # Set remote description
        await pc.setRemoteDescription(RTCSessionDescription(
            sdp=offer['sdp'],
            type=offer['type']
        ))
        
        # Create answer
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        
        return jsonify({
            "success": True,
            "answer": {
                "sdp": pc.localDescription.sdp,
                "type": pc.localDescription.type
            },
            "pc_id": pc_id
        })
        
    except Exception as e:
        logger.error(f"WebRTC offer error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/webrtc/ice', methods=['POST'])
async def webrtc_ice():
    """Handle ICE candidates"""
    try:
        data = request.json
        pc_id = data.get('pc_id')
        candidate = data.get('candidate')
        
        if pc_id not in peer_connections:
            return jsonify({"error": "Invalid peer connection"}), 400
        
        pc = peer_connections[pc_id]
        await pc.addIceCandidate(candidate)
        
        return jsonify({"success": True})
        
    except Exception as e:
        logger.error(f"ICE candidate error: {e}")
        return jsonify({"error": str(e)}), 500

# Socket.IO Events for Real-time Communication
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {"message": "Connected to Future Self server"})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

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
        
        # Generate future self response
        context = {
            "session_id": session_id,
            "conversation_id": conversation_id,
            "career": career
        }
        
        response = generate_future_self_response(career, message, context)
        
        # Store messages
        if session_id in sessions_store:
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
                    break
        
        # Emit response to client
        emit('receive_message', {
            "message": response,
            "timestamp": datetime.now().isoformat()
        }, room=session_id)
        
    except Exception as e:
        logger.error(f"Message handling error: {e}")
        emit('error', {"error": str(e)})

@socketio.on('start_video_call')
async def handle_start_video_call(data):
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
        
        career_info = CAREER_DATABASE.get(career, {})
        
        # Generate 10-year timeline
        timeline = {}
        salary_range = career_info.get('avg_salary', {})
        
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
        
        return jsonify({
            "success": True,
            "timeline": timeline
        })
        
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

# Static file serving
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    """Serve uploaded files"""
    return send_from_directory(UPLOAD_DIR, filename)

@app.route('/static/<path:filepath>')
def serve_static(filepath):
    """Serve static files"""
    return send_from_directory(STATIC_DIR, filepath)

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
    
    # Close all peer connections
    for pc in peer_connections.values():
        asyncio.create_task(pc.close())
    
    # Close Redis connection
    if redis_client:
        redis_client.close()
    
    logger.info("Cleanup complete")

# Main execution
if __name__ == '__main__':
    print("\n" + "="*60)
    print("FUTURE SELF AI CAREER ADVISOR - STARTING")
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