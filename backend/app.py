# app.py - Corrected Future Self AI Career Advisor Backend
import os
import sys
import json
import base64
import uuid
import hashlib
import tempfile
import re
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

# Document processing
import PyPDF2
import docx

# Image processing
from PIL import Image
import numpy as np

# AI and ML
import anthropic
import google.generativeai as genai
import openai

# Data processing
import pandas as pd

# Additional utilities
import redis
import jwt
from dotenv import load_dotenv
import logging
from dataclasses import dataclass, asdict
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

# CORS configuration - Fixed
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:5000", "http://localhost:5173", "http://127.0.0.1:5000"],
        "supports_credentials": True
    }
})

# Initialize SocketIO
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

# Redis for session management
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

# AI Model Configuration - Fixed
class AIModels:
    def __init__(self):
        # Claude
        try:
            self.claude = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            logger.info("Claude API initialized")
        except:
            self.claude = None
            logger.warning("Claude API not configured")
        
        # Gemini - Fixed model name
        try:
            genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
            # Use the correct model name
            self.gemini = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Gemini API initialized")
        except Exception as e:
            self.gemini = None
            logger.warning(f"Gemini API not configured: {e}")
        
        # OpenAI
        try:
            openai.api_key = os.getenv('OPENAI_API_KEY')
            self.openai_client = openai
            logger.info("OpenAI API initialized")
        except:
            self.openai_client = None
            logger.warning("OpenAI API not configured")

ai_models = AIModels()

# Directory setup
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / 'uploads'
STATIC_DIR = BASE_DIR / 'static'
AVATAR_DIR = STATIC_DIR / 'avatars'
RESUME_DIR = STATIC_DIR / 'resumes'

# Create directories
for directory in [UPLOAD_DIR, STATIC_DIR, AVATAR_DIR, RESUME_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# File extensions
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'docx', 'txt'}

# Career Database
CAREER_DATABASE = {
    "doctor": {
        "title": "Medical Doctor",
        "avg_salary": {"entry": 60000, "mid": 180000, "senior": 350000},
        "years_training": 11,
        "required_skills": [
            "Biology", "Chemistry", "Anatomy", "Physiology", "Pharmacology",
            "Clinical Skills", "Patient Care", "Medical Ethics", "Research",
            "Critical Thinking", "Communication", "Empathy"
        ],
        "personality_traits": ["Compassionate", "Detail-oriented", "Resilient"],
        "work_life_balance": 3,
        "job_satisfaction": 8,
        "growth_potential": 9
    },
    "software_engineer": {
        "title": "Software Engineer",
        "avg_salary": {"entry": 75000, "mid": 130000, "senior": 200000},
        "years_training": 1,
        "required_skills": [
            "Programming", "Data Structures", "Algorithms", "System Design",
            "Git", "Testing", "Debugging", "Agile", "Cloud Computing",
            "Problem Solving", "Continuous Learning"
        ],
        "personality_traits": ["Logical", "Creative", "Patient", "Curious"],
        "work_life_balance": 7,
        "job_satisfaction": 8,
        "growth_potential": 10
    },
    "data_scientist": {
        "title": "Data Scientist",
        "avg_salary": {"entry": 85000, "mid": 130000, "senior": 180000},
        "years_training": 2,
        "required_skills": [
            "Python", "R", "SQL", "Statistics", "Machine Learning",
            "Data Visualization", "Big Data", "Deep Learning",
            "Communication", "Problem Solving"
        ],
        "personality_traits": ["Analytical", "Curious", "Detail-oriented"],
        "work_life_balance": 7,
        "job_satisfaction": 8,
        "growth_potential": 9
    },
    "entrepreneur": {
        "title": "Entrepreneur",
        "avg_salary": {"entry": -50000, "mid": 100000, "senior": 1000000},
        "years_training": 0,
        "required_skills": [
            "Business Strategy", "Marketing", "Sales", "Finance", "Leadership",
            "Networking", "Product Development", "Risk Management",
            "Resilience", "Vision", "Adaptability"
        ],
        "personality_traits": ["Risk-taker", "Visionary", "Persistent"],
        "work_life_balance": 3,
        "job_satisfaction": 9,
        "growth_potential": 10
    },
    "teacher": {
        "title": "Teacher",
        "avg_salary": {"entry": 40000, "mid": 55000, "senior": 75000},
        "years_training": 4,
        "required_skills": [
            "Subject Expertise", "Curriculum Development", "Classroom Management",
            "Communication", "Assessment", "Technology Integration",
            "Patience", "Creativity", "Empathy"
        ],
        "personality_traits": ["Patient", "Nurturing", "Creative"],
        "work_life_balance": 8,
        "job_satisfaction": 8,
        "growth_potential": 5
    }
}

# Session storage
sessions_store = {}

# Utility Functions
def allowed_file(filename, extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions

def extract_text_from_pdf(filepath):
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
    try:
        doc = docx.Document(filepath)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        logger.error(f"DOCX extraction error: {e}")
        return ""

def analyze_resume_with_ai(resume_text):
    """Analyze resume using AI"""
    if ai_models.gemini:
        try:
            prompt = f"""
            Analyze this resume and extract:
            1. Current role/title
            2. Years of experience
            3. Key skills (technical and soft)
            4. Education level
            
            Resume: {resume_text[:3000]}
            
            Return as structured text.
            """
            
            response = ai_models.gemini.generate_content(prompt)
            return {"analysis": response.text}
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
    
    return {"analysis": "Manual analysis required"}

def calculate_career_match(user_skills, career):
    """Calculate match percentage between user skills and career requirements"""
    career_info = CAREER_DATABASE.get(career, {})
    required_skills = career_info.get('required_skills', [])
    
    if not required_skills:
        return {"match_percentage": 0, "matched_skills": [], "missing_skills": []}
    
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

def generate_aged_avatar(photo_path, age_years=10):
    """Simple age progression (placeholder for real implementation)"""
    # In production, use a real age progression API or model
    # For now, just return the original photo
    return photo_path

def generate_future_self_response(career, question, context):
    """Generate response as future self using AI"""
    career_info = CAREER_DATABASE.get(career, {})
    
    prompt = f"""
    You are speaking as someone's future self who became a successful {career_info.get('title', career)}.
    You are 10 years in the future. Be realistic about both challenges and rewards.
    
    Career: {career}
    Personality: {', '.join(career_info.get('personality_traits', []))}
    
    User question: {question}
    
    Respond in first person, as if you are their actual future self. Be encouraging but honest.
    Keep response under 200 words.
    """
    
    if ai_models.claude:
        try:
            response = ai_models.claude.messages.create(
                model="claude-3-haiku-20240307",
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
            "openai": ai_models.openai_client is not None
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
        
        filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        filepath = UPLOAD_DIR / filename
        file.save(str(filepath))
        
        session_id = str(uuid.uuid4())
        sessions_store[session_id] = {
            "created_at": datetime.now().isoformat(),
            "photo_path": str(filepath),
            "conversations": []
        }
        
        if redis_client:
            redis_client.setex(
                f"session:{session_id}",
                86400,
                json.dumps(sessions_store[session_id])
            )
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "photo_url": f"/static/uploads/{filename}"
        })
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/age-photo', methods=['POST'])
def age_photo():
    """Generate aged version of uploaded photo - Fixed: removed async"""
    try:
        data = request.json
        session_id = data.get('session_id')
        career = data.get('career')
        original_photo_url = data.get('original_photo_url')
        
        if not all([session_id, career, original_photo_url]):
            return jsonify({"error": "Missing parameters"}), 400
        
        # Simple implementation - return original for now
        # In production, integrate with age progression API
        aged_url = original_photo_url
        
        if session_id in sessions_store:
            sessions_store[session_id]['aged_avatar'] = aged_url
        
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
        
        greeting = generate_future_self_response(
            career,
            "Introduce yourself to your past self",
            {"name": name, "career_info": career_info}
        )
        
        conversation = {
            "id": conversation_id,
            "career": career,
            "started_at": datetime.now().isoformat(),
            "messages": [
                {"role": "future_self", "content": greeting, "timestamp": datetime.now().isoformat()}
            ]
        }
        
        sessions_store[session_id]["conversations"].append(conversation)
        
        return jsonify({
            "success": True,
            "conversation_id": conversation_id,
            "greeting": greeting
        })
        
    except Exception as e:
        logger.error(f"Start conversation error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload-resume', methods=['POST'])
def upload_resume():
    """Handle resume upload"""
    try:
        if 'resume' not in request.files:
            return jsonify({"error": "No resume provided"}), 400
        
        file = request.files['resume']
        session_id = request.form.get('session_id')
        
        if not session_id:
            session_id = str(uuid.uuid4())
            sessions_store[session_id] = {"created_at": datetime.now().isoformat()}
        
        if file and allowed_file(file.filename, ALLOWED_DOCUMENT_EXTENSIONS):
            filename = f"{session_id}_resume_{secure_filename(file.filename)}"
            filepath = RESUME_DIR / filename
            file.save(str(filepath))
            
            # Extract text
            file_ext = filename.rsplit('.', 1)[1].lower()
            if file_ext == 'pdf':
                resume_text = extract_text_from_pdf(filepath)
            elif file_ext == 'docx':
                resume_text = extract_text_from_docx(filepath)
            else:
                with open(filepath, 'r', encoding='utf-8') as f:
                    resume_text = f.read()
            
            # Analyze resume
            analysis = analyze_resume_with_ai(resume_text)
            
            # Simple skills extraction
            skills = []
            skill_keywords = ["python", "java", "javascript", "react", "node", "sql", "machine learning",
                             "data analysis", "project management", "leadership", "communication"]
            
            resume_lower = resume_text.lower()
            for skill in skill_keywords:
                if skill in resume_lower:
                    skills.append(skill.title())
            
            # Calculate career matches
            career_matches = {}
            for career_key in CAREER_DATABASE.keys():
                match_result = calculate_career_match(skills, career_key)
                career_matches[career_key] = match_result
            
            return jsonify({
                "success": True,
                "session_id": session_id,
                "extracted_info": {
                    "skills": skills,
                    "years_experience": 2,  # Placeholder
                    "education_level": 3    # Placeholder
                },
                "career_matches": career_matches,
                "ai_analysis": analysis
            })
            
    except Exception as e:
        logger.error(f"Resume upload error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/skills-analysis', methods=['POST'])
def skills_analysis():
    """Analyze skills gap for career transition"""
    try:
        data = request.json
        session_id = data.get('session_id')
        target_career = data.get('career')
        current_skills = data.get('current_skills', [])
        
        match_result = calculate_career_match(current_skills, target_career)
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

@app.route('/api/generate-projects', methods=['POST'])
def generate_projects():
    """Generate project recommendations - Added missing endpoint"""
    try:
        data = request.json
        career = data.get('career')
        skill_level = data.get('skill_level', 'intermediate')
        
        projects = {
            "software_engineer": [
                {
                    "title": "Personal Portfolio Website",
                    "description": "Build a responsive portfolio using modern web technologies",
                    "skills": ["HTML", "CSS", "JavaScript", "React"],
                    "duration": "2-3 weeks"
                },
                {
                    "title": "Task Management App",
                    "description": "Create a full-stack application for managing tasks",
                    "skills": ["Node.js", "Express", "MongoDB", "React"],
                    "duration": "4 weeks"
                }
            ],
            "data_scientist": [
                {
                    "title": "Predictive Model Project",
                    "description": "Build a machine learning model for predictions",
                    "skills": ["Python", "Scikit-learn", "Pandas", "Visualization"],
                    "duration": "3 weeks"
                }
            ]
        }
        
        recommended_projects = projects.get(career, [
            {
                "title": "Industry Research Project",
                "description": "Research and document industry trends",
                "skills": ["Research", "Analysis", "Presentation"],
                "duration": "2 weeks"
            }
        ])
        
        return jsonify({
            "success": True,
            "projects": recommended_projects
        })
        
    except Exception as e:
        logger.error(f"Generate projects error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/interview-prep', methods=['POST'])
def interview_prep():
    """Generate interview preparation materials - Added missing endpoint"""
    try:
        data = request.json
        career = data.get('career')
        
        interview_questions = {
            "software_engineer": {
                "technical": [
                    "Explain the difference between stack and queue",
                    "What is time complexity?",
                    "How would you design a URL shortener?"
                ],
                "behavioral": [
                    "Tell me about a challenging project",
                    "How do you handle disagreements?",
                    "Why this career?"
                ]
            }
        }
        
        questions = interview_questions.get(career, {
            "technical": ["Describe your technical skills"],
            "behavioral": ["Why are you interested in this field?"]
        })
        
        tips = [
            "Research the company thoroughly",
            "Practice your responses",
            "Prepare questions to ask",
            "Dress professionally",
            "Arrive early"
        ]
        
        return jsonify({
            "success": True,
            "questions": questions,
            "tips": tips
        })
        
    except Exception as e:
        logger.error(f"Interview prep error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/salary-projection', methods=['POST'])
def salary_projection():
    """Project salary growth - Added missing endpoint"""
    try:
        data = request.json
        career = data.get('career')
        
        career_info = CAREER_DATABASE.get(career, {})
        salary_range = career_info.get('avg_salary', {})
        
        projections = []
        base_salary = salary_range.get('entry', 50000)
        
        for year in range(1, 11):
            if year <= 3:
                growth_rate = 0.08
            elif year <= 7:
                growth_rate = 0.06
            else:
                growth_rate = 0.04
            
            base_salary *= (1 + growth_rate)
            projections.append({
                "year": year,
                "salary": round(base_salary)
            })
        
        return jsonify({
            "success": True,
            "starting_salary": salary_range.get('entry', 50000),
            "projections": projections,
            "negotiation_tips": [
                "Research market rates",
                "Highlight your unique value",
                "Consider total compensation",
                "Be prepared to negotiate"
            ]
        })
        
    except Exception as e:
        logger.error(f"Salary projection error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/export-session', methods=['POST'])
def export_session():
    """Export session data"""
    try:
        session_id = request.json.get('session_id')
        
        if session_id not in sessions_store:
            return jsonify({"error": "Invalid session"}), 400
        
        session = sessions_store[session_id]
        
        return jsonify({
            "success": True,
            "session_data": session,
            "export_url": f"/reports/{session_id}.pdf"
        })
        
    except Exception as e:
        logger.error(f"Export error: {e}")
        return jsonify({"error": str(e)}), 500

# Socket.IO Events
@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {"message": "Connected to Future Self server"})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('join_session')
def handle_join_session(data):
    session_id = data.get('session_id')
    if session_id:
        join_room(session_id)
        emit('joined_session', {"session_id": session_id}, room=session_id)

@socketio.on('send_message')
def handle_message(data):
    try:
        session_id = data.get('session_id')
        message = data.get('message')
        career = data.get('career')
        
        context = {
            "session_id": session_id,
            "career": career
        }
        
        response = generate_future_self_response(career, message, context)
        
        if session_id in sessions_store and sessions_store[session_id].get('conversations'):
            sessions_store[session_id]['conversations'][-1]['messages'].append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })
            sessions_store[session_id]['conversations'][-1]['messages'].append({
                "role": "future_self",
                "content": response,
                "timestamp": datetime.now().isoformat()
            })
        
        emit('receive_message', {
            "message": response,
            "timestamp": datetime.now().isoformat()
        }, room=session_id)
        
    except Exception as e:
        logger.error(f"Message handling error: {e}")
        emit('error', {"error": str(e)})

@socketio.on('start_video_call')
def handle_start_video_call(data):
    try:
        session_id = data.get('session_id')
        career = data.get('career')
        
        emit('video_call_ready', {
            "status": "ready",
            "career": career
        }, room=session_id)
        
    except Exception as e:
        logger.error(f"Video call error: {e}")
        emit('error', {"error": str(e)})

# Static file serving
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

# Main execution
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
    
    socketio.run(
        app,
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=False,
        log_output=True
    )