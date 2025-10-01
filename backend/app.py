# app_structured.py - Future Self AI Career Advisor Backend
import os
import sys
import json
import uuid
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
sys.path.append(current_dir)

# Import services
from services.session_service import SessionService
from services.personalized_ai import personalized_ai_service
from services.rag_pipeline import rag_pipeline
from services.basic_rag import basic_rag
from model.career_database import career_database
from services.resume_analyzer import (
    ResumeAnalyzer, 
    extract_text_from_pdf, 
    extract_text_from_docx,
    calculate_career_match
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder=os.path.join(project_root, 'frontend', 'build'), static_url_path='')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Setup CORS
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        "supports_credentials": True
    }
})

# Initialize SocketIO with CORS support
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=False,
    async_mode='threading',
    ping_timeout=60,
    ping_interval=25,
    allow_upgrades=True
)

# Setup rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Initialize services
session_service = SessionService()
resume_analyzer = ResumeAnalyzer()

# File upload configuration
UPLOAD_FOLDER = Path(current_dir) / 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}
UPLOAD_FOLDER.mkdir(exist_ok=True)

# Store active connections
active_connections = {}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_session_id():
    """Generate unique session ID"""
    return str(uuid.uuid4())

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    client_id = request.sid
    logger.info(f"Client connected: {client_id}")
    active_connections[client_id] = {
        'connected_at': datetime.now().isoformat(),
        'session_id': None
    }
    emit('connected', {
        'status': 'connected',
        'client_id': client_id,
        'message': 'Connected to Future Self AI'
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    client_id = request.sid
    logger.info(f"Client disconnected: {client_id}")
    if client_id in active_connections:
        del active_connections[client_id]

@socketio.on('join_session')
def handle_join_session(data):
    """Join a chat session room"""
    client_id = request.sid
    session_id = data.get('session_id')
    
    logger.info(f"Join session request from {client_id} for session {session_id}")
    
    if not session_id:
        logger.error("No session ID provided")
        emit('error', {'error': 'Session ID required', 'message': 'Session ID required'})
        return
    
    # Create session if it doesn't exist
    session_data = session_service.get_session(session_id)
    if not session_data:
        logger.info(f"Creating new session for {session_id}")
        session_data = {
            'session_id': session_id,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'status': 'active',
            'conversation_history': [],
            'persona': {}
        }
        session_service.create_session(session_data)
    
    # Join the room
    join_room(session_id)
    
    # Update connection info
    if client_id in active_connections:
        active_connections[client_id]['session_id'] = session_id
    
    logger.info(f"Client {client_id} joined session {session_id} successfully")
    
    emit('session_joined', {
        'session_id': session_id,
        'status': 'joined',
        'message': 'Joined chat session successfully'
    })

@socketio.on('leave_session')
def handle_leave_session(data):
    """Leave a chat session room"""
    client_id = request.sid
    session_id = data.get('session_id')
    
    if session_id:
        leave_room(session_id)
        logger.info(f"Client {client_id} left session {session_id}")
        
        emit('session_left', {
            'session_id': session_id,
            'status': 'left'
        })

@socketio.on('message')
def handle_message(data):
    """Handle chat messages from frontend"""
    client_id = request.sid
    session_id = data.get('session_id')
    message = data.get('message', '').strip()
    frontend_conversation_history = data.get('conversation_history', [])
    
    logger.info(f"Message received from {client_id}: {message[:50]}...")
    
    if not session_id or not message:
        emit('error', {'error': 'Session ID and message required'})
        return
    
    # Get session data
    session_data = session_service.get_session(session_id)
    if not session_data:
        logger.info(f"Creating session data for {session_id}")
        session_data = {
            'session_id': session_id,
            'conversation_history': [],
            'persona': {},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        session_service.create_session(session_data)
    
    # Get persona and conversation history
    persona = session_data.get('persona', {})
    conversation_history = session_data.get('conversation_history', [])
    
    # Use frontend conversation history if available and more recent
    if frontend_conversation_history and len(frontend_conversation_history) > len(conversation_history):
        logger.info(f"Using frontend conversation history with {len(frontend_conversation_history)} messages")
        conversation_history = frontend_conversation_history
    
    # Send typing indicator
    emit('typing', {'status': 'start'}, room=session_id)
    
    try:
        # Generate AI response with RAG context
        logger.info(f"Generating AI response for session {session_id}")
        
        # Get relevant context from RAG if available
        rag_context = ""
        if basic_rag.get_document_count() > 0:
            try:
                rag_context = basic_rag.retrieve_context(message, top_k=2)
                logger.info(f"Retrieved RAG context: {len(rag_context)} characters")
            except Exception as e:
                logger.warning(f"Failed to retrieve RAG context: {e}")
                rag_context = ""
        
        # Add RAG context to persona for enhanced responses
        enhanced_persona = persona.copy()
        if rag_context and rag_context != "No relevant documents found.":
            enhanced_persona['rag_context'] = rag_context
        
        ai_response = personalized_ai_service.generate_response(
            message=message,
            persona=enhanced_persona,
            session_id=session_id,
            conversation_history=conversation_history
        )
        
        # Stop typing indicator
        emit('typing', {'status': 'stop'}, room=session_id)
        
        # Only send response if Gemini generated one
        if ai_response is not None:
            # Update conversation history
            conversation_history.append({
                'role': 'user',
                'content': message,
                'timestamp': datetime.now().isoformat()
            })
            
            conversation_history.append({
                'role': 'assistant',
                'content': ai_response,
                'timestamp': datetime.now().isoformat()
            })
            
            # Keep only last 20 messages
            if len(conversation_history) > 20:
                conversation_history = conversation_history[-20:]
            
            # Update session
            session_data['conversation_history'] = conversation_history
            session_data['updated_at'] = datetime.now().isoformat()
            session_service.update_session(session_id, session_data)
            
            # Send response - using 'ai_response' event name to match frontend
            logger.info(f"Sending AI response to client")
            emit('ai_response', {
                'response': ai_response,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            })
        else:
            logger.warning(f"No response generated for session {session_id} - Gemini unavailable")
            # Don't send any response, let the client handle the silence
        
    except Exception as e:
        logger.error(f"Chat message error: {e}", exc_info=True)
        emit('typing', {'status': 'stop'}, room=session_id)
        emit('error', {
            'error': 'Failed to generate response',
            'message': str(e)
        })

@socketio.on('ping')
def handle_ping():
    """Handle ping for connection keep-alive"""
    emit('pong', {'timestamp': datetime.now().isoformat()})

# REST API endpoints
@app.route('/')
def serve_frontend():
    """Serve React frontend"""
    frontend_path = os.path.join(project_root, 'frontend', 'build', 'index.html')
    if os.path.exists(frontend_path):
        return send_from_directory(os.path.join(project_root, 'frontend', 'build'), 'index.html')
    else:
        return jsonify({"message": "Future Self AI API is running. Frontend not built."}), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    services_status = {
        'api': 'healthy',
        'personalized_ai': personalized_ai_service.is_model_available(),
        'basic_rag': basic_rag.get_stats(),
        'gemini': bool(os.getenv('GEMINI_API_KEY')),
        'sessions': session_service.is_healthy(),
        'websocket': len(active_connections),
        'timestamp': datetime.now().isoformat()
    }
    
    overall_health = all([
        services_status['api'] == 'healthy',
        services_status['sessions']
    ])
    
    return jsonify({
        'status': 'healthy' if overall_health else 'degraded',
        'services': services_status,
        'active_connections': len(active_connections)
    }), 200 if overall_health else 503

@app.route('/api/init-session', methods=['POST'])
@limiter.limit("30 per hour")
def init_session():
    """Initialize a new session"""
    try:
        session_id = generate_session_id()
        timestamp = datetime.now().isoformat()
        
        session_data = {
            'session_id': session_id,
            'created_at': timestamp,
            'updated_at': timestamp,
            'status': 'active',
            'persona': None,
            'resume_analysis': None,
            'conversation_history': []
        }
        
        session_service.create_session(session_data)
        
        logger.info(f"Session initialized: {session_id}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Session initialized successfully'
        })
    except Exception as e:
        logger.error(f"Session initialization error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-resume', methods=['POST'])
@limiter.limit("10 per hour")
def analyze_resume():
    """Analyze uploaded resume with enhanced analysis"""
    try:
        # Validate request
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file provided'}), 400
        
        file = request.files['resume']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload PDF, DOCX, or TXT'}), 400
        
        # Get session ID and career goal
        session_id = request.form.get('session_id', generate_session_id())
        career_goal = request.form.get('career_goal', '').lower().replace(' ', '_')
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{session_id}_{timestamp}_{filename}"
        filepath = UPLOAD_FOLDER / unique_filename
        file.save(str(filepath))
        
        logger.info(f"Resume saved: {unique_filename}")
        
        # Extract text based on file type
        try:
            if filename.lower().endswith('.pdf'):
                resume_text = extract_text_from_pdf(str(filepath))
            elif filename.lower().endswith(('.docx', '.doc')):
                resume_text = extract_text_from_docx(str(filepath))
            else:
                with open(str(filepath), 'r', encoding='utf-8', errors='ignore') as f:
                    resume_text = f.read()
        except Exception as e:
            logger.error(f"Text extraction error: {e}")
            return jsonify({'error': 'Failed to extract text from file'}), 500
        
        # Validate extracted text
        if not resume_text or len(resume_text) < 50:
            return jsonify({'error': 'Could not extract sufficient text from resume'}), 400
        
        # Enhanced resume analysis
        logger.info("Starting enhanced resume analysis...")
        resume_analysis = resume_analyzer.analyze_resume(resume_text, career_goal)
        
        # Create persona based on analysis
        logger.info("Creating future self persona...")
        persona = personalized_ai_service.create_future_self_persona(
            resume_analysis, 
            career_goal if career_goal else resume_analysis.get('detected_career', 'software_engineer')
        )
        
        # Add additional insights to persona
        if 'gemini_insights' in resume_analysis:
            persona['ai_insights'] = resume_analysis['gemini_insights']
        
        # Ensure backward compatibility
        if 'extracted_info' not in resume_analysis:
            resume_analysis['extracted_info'] = {
                'skills': resume_analyzer._flatten_skills(resume_analysis.get('skills', {})),
                'years_experience': resume_analysis.get('years_experience', 0),
                'education_level': resume_analysis.get('education_level', 0),
                'personal_info': resume_analysis.get('personal_info', {})
            }
        
        # Store in session
        session_data = {
            'session_id': session_id,
            'resume_analysis': resume_analysis,
            'persona': persona,
            'career_goal': career_goal if career_goal else resume_analysis.get('detected_career'),
            'updated_at': datetime.now().isoformat(),
            'conversation_history': []
        }
        
        session_service.update_session(session_id, session_data)
        
        # Prepare response
        response_data = {
            'success': True,
            'session_id': session_id,
            'persona': persona,
            'resume_analysis': resume_analysis,
            'extracted_info': resume_analysis.get('extracted_info'),
            'skills': resume_analysis.get('skills'),
            'career_match': resume_analysis.get('career_match'),
            'career_insights': resume_analysis.get('career_insights'),
            'detected_career': resume_analysis.get('detected_career'),
            'years_experience': resume_analysis.get('years_experience', 0),
            'education_level': resume_analysis.get('education_level', 0),
            'analysis_method': resume_analysis.get('analysis_method', 'Pattern Matching'),
            'message': 'Resume analyzed successfully!'
        }
        
        logger.info(f"Resume analysis completed for session {session_id}")
        logger.info(f"Detected career: {resume_analysis.get('detected_career')}")
        logger.info(f"Skills found: {len(resume_analysis.get('extracted_info', {}).get('skills', []))}")
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Resume analysis error: {str(e)}", exc_info=True)
        return jsonify({
            'error': f'Failed to analyze resume: {str(e)}',
            'success': False
        }), 500

@app.route('/api/update-career-goal', methods=['POST'])
@limiter.limit("30 per hour")
def update_career_goal():
    """Update career goal and recalculate match"""
    try:
        data = request.json
        session_id = data.get('session_id')
        career_goal = data.get('career_goal', '').lower().replace(' ', '_')
        
        if not session_id:
            return jsonify({'error': 'Session ID required'}), 400
        
        # Get session data
        session_data = session_service.get_session(session_id)
        if not session_data:
            return jsonify({'error': 'Session not found'}), 404
        
        # Update career goal
        resume_analysis = session_data.get('resume_analysis', {})
        
        # Recalculate career match with new goal
        if resume_analysis:
            skills = resume_analysis.get('skills', {})
            years_exp = resume_analysis.get('years_experience', 0)
            
            new_career_match = resume_analyzer._calculate_career_match(
                skills, career_goal, years_exp
            )
            
            resume_analysis['career_match'] = new_career_match
            resume_analysis['selected_career'] = career_goal
        
        # Update persona
        persona = personalized_ai_service.create_future_self_persona(
            resume_analysis, career_goal
        )
        
        # Update session
        session_data['career_goal'] = career_goal
        session_data['resume_analysis'] = resume_analysis
        session_data['persona'] = persona
        session_data['updated_at'] = datetime.now().isoformat()
        
        session_service.update_session(session_id, session_data)
        
        return jsonify({
            'success': True,
            'career_goal': career_goal,
            'career_match': new_career_match,
            'persona': persona,
            'message': 'Career goal updated successfully'
        })
            
    except Exception as e:
        logger.error(f"Career goal update error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
@limiter.limit("100 per hour")
def chat():
    """Chat with future self AI (REST fallback)"""
    try:
        data = request.json
        session_id = data.get('session_id')
        message = data.get('message', '').strip()
        frontend_conversation_history = data.get('conversation_history', [])
        
        if not session_id:
            return jsonify({'error': 'Session ID required'}), 400
        
        if not message:
            return jsonify({'error': 'Message required'}), 400
        
        # Get session data
        session_data = session_service.get_session(session_id)
        if not session_data:
            # Create minimal session if doesn't exist
            session_data = {
                'session_id': session_id,
                'persona': {},
                'conversation_history': [],
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            session_service.create_session(session_data)
        
        # Get persona and conversation history
        persona = session_data.get('persona', {})
        conversation_history = session_data.get('conversation_history', [])
        
        # Use frontend conversation history if available and more recent
        if frontend_conversation_history and len(frontend_conversation_history) > len(conversation_history):
            logger.info(f"Using frontend conversation history with {len(frontend_conversation_history)} messages")
            conversation_history = frontend_conversation_history
        
        # Generate response using enhanced AI with RAG context
        logger.info(f"Generating AI response for session {session_id}")
        
        # Get relevant context from RAG if available
        rag_context = ""
        if basic_rag.get_document_count() > 0:
            try:
                rag_context = basic_rag.retrieve_context(message, top_k=2)
                logger.info(f"Retrieved RAG context: {len(rag_context)} characters")
            except Exception as e:
                logger.warning(f"Failed to retrieve RAG context: {e}")
                rag_context = ""
        
        # Add RAG context to persona for enhanced responses
        enhanced_persona = persona.copy()
        if rag_context and rag_context != "No relevant documents found.":
            enhanced_persona['rag_context'] = rag_context
        
        ai_response = personalized_ai_service.generate_response(
            message=message,
            persona=enhanced_persona,
            session_id=session_id,
            conversation_history=conversation_history
        )
        
        # Only update history and return response if Gemini generated one
        if ai_response is not None:
            # Update conversation history
            conversation_history.append({
                'role': 'user',
                'content': message,
                'timestamp': datetime.now().isoformat()
            })
            
            conversation_history.append({
                'role': 'assistant',
                'content': ai_response,
                'timestamp': datetime.now().isoformat()
            })
            
            # Keep only last 20 messages to avoid token limits
            if len(conversation_history) > 20:
                conversation_history = conversation_history[-20:]
            
            # Update session
            session_data['conversation_history'] = conversation_history
            session_data['updated_at'] = datetime.now().isoformat()
            session_service.update_session(session_id, session_data)
            
            return jsonify({
                'success': True,
                'response': ai_response,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            })
        else:
            logger.warning(f"No response generated for session {session_id} - Gemini unavailable")
            return jsonify({
                'success': False,
                'error': 'No response available',
                'message': 'Gemini AI is currently unavailable',
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            }), 503
        
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        return jsonify({
            'error': 'Failed to generate response',
            'success': False
        }), 500

@app.route('/api/get-session', methods=['GET'])
@limiter.limit("100 per hour")
def get_session():
    """Get session data"""
    try:
        session_id = request.args.get('session_id')
        
        if not session_id:
            return jsonify({'error': 'Session ID required'}), 400
        
        session_data = session_service.get_session(session_id)
        
        if not session_data:
            return jsonify({'error': 'Session not found'}), 404
        
        return jsonify({
            'success': True,
            'session_data': session_data
        })
        
    except Exception as e:
        logger.error(f"Get session error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/career-database', methods=['GET'])
def get_career_database():
    """Get available careers and their requirements"""
    try:
        return jsonify({
            'success': True,
            'careers': career_database.get_all_careers(),
            'categories': career_database.get_career_categories()
        })
    except Exception as e:
        logger.error(f"Career database error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/career-details/<career_id>', methods=['GET'])
def get_career_details(career_id):
    """Get detailed information about a specific career"""
    try:
        career = career_database.get_career(career_id)
        if not career:
            return jsonify({'error': 'Career not found'}), 404
        
        return jsonify({
            'success': True,
            'career': career
        })
    except Exception as e:
        logger.error(f"Career details error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/learning-resources', methods=['POST'])
@limiter.limit("50 per hour")
def get_learning_resources():
    """Get learning resources based on skills gap"""
    try:
        data = request.json
        missing_skills = data.get('missing_skills', [])
        career_goal = data.get('career_goal', 'software_engineer')
        
        # Use RAG pipeline if available
        if rag_pipeline and rag_pipeline.is_available():
            resources = rag_pipeline.get_learning_resources(missing_skills, career_goal)
        else:
            # Fallback to basic recommendations
            resources = {
                'courses': [
                    {
                        'title': f"Learn {skill}",
                        'platform': 'Online Learning',
                        'duration': '4-6 weeks',
                        'level': 'Beginner to Intermediate'
                    }
                    for skill in missing_skills[:5]
                ],
                'tutorials': [
                    f"{skill} Tutorial" for skill in missing_skills[:3]
                ],
                'projects': [
                    f"Build a {career_goal.replace('_', ' ')} project using {missing_skills[0] if missing_skills else 'modern tools'}"
                ]
            }
        
        return jsonify({
            'success': True,
            'resources': resources
        })
    except Exception as e:
        logger.error(f"Learning resources error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export-session', methods=['GET'])
@limiter.limit("20 per hour")
def export_session():
    """Export session data for user download"""
    try:
        session_id = request.args.get('session_id')
        format_type = request.args.get('format', 'json')
        
        if not session_id:
            return jsonify({'error': 'Session ID required'}), 400
        
        session_data = session_service.get_session(session_id)
        if not session_data:
            return jsonify({'error': 'Session not found'}), 404
        
        # Prepare export data
        export_data = {
            'session_id': session_id,
            'exported_at': datetime.now().isoformat(),
            'persona': session_data.get('persona'),
            'resume_analysis': session_data.get('resume_analysis'),
            'career_goal': session_data.get('career_goal'),
            'conversation_history': session_data.get('conversation_history', [])
        }
        
        if format_type == 'json':
            return jsonify(export_data)
        else:
            return jsonify({'error': 'Unsupported format'}), 400
        
    except Exception as e:
        logger.error(f"Export session error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/feedback', methods=['POST'])
@limiter.limit("20 per hour")
def submit_feedback():
    """Submit user feedback"""
    try:
        data = request.json
        session_id = data.get('session_id')
        feedback_type = data.get('type', 'general')
        feedback_text = data.get('feedback', '')
        rating = data.get('rating', 0)
        
        # Store feedback (implement your storage mechanism)
        feedback_data = {
            'session_id': session_id,
            'type': feedback_type,
            'feedback': feedback_text,
            'rating': rating,
            'timestamp': datetime.now().isoformat()
        }
        
        # Log feedback for now
        logger.info(f"Feedback received: {feedback_data}")
        
        return jsonify({
            'success': True,
            'message': 'Thank you for your feedback!'
        })
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        return jsonify({'error': str(e)}), 500

# Basic RAG API endpoints
@app.route('/api/rag/search', methods=['POST'])
@limiter.limit("50 per hour")
def rag_search():
    """Search documents using basic RAG"""
    try:
        data = request.json
        query = data.get('query', '').strip()
        top_k = data.get('top_k', 5)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Search using basic RAG
        results = basic_rag.search(query, top_k)
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'total_found': len(results)
        })
        
    except Exception as e:
        logger.error(f"RAG search error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rag/add-document', methods=['POST'])
@limiter.limit("30 per hour")
def rag_add_document():
    """Add a document to the RAG knowledge base"""
    try:
        data = request.json
        content = data.get('content', '').strip()
        metadata = data.get('metadata', {})
        
        if not content:
            return jsonify({'error': 'Document content is required'}), 400
        
        # Add document to RAG
        basic_rag.add_document(content, metadata)
        
        return jsonify({
            'success': True,
            'message': 'Document added successfully',
            'total_documents': basic_rag.get_document_count()
        })
        
    except Exception as e:
        logger.error(f"RAG add document error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rag/add-documents', methods=['POST'])
@limiter.limit("20 per hour")
def rag_add_documents():
    """Add multiple documents to the RAG knowledge base"""
    try:
        data = request.json
        documents = data.get('documents', [])
        
        if not documents or not isinstance(documents, list):
            return jsonify({'error': 'Documents array is required'}), 400
        
        # Add documents to RAG
        basic_rag.add_documents(documents)
        
        return jsonify({
            'success': True,
            'message': f'{len(documents)} documents added successfully',
            'total_documents': basic_rag.get_document_count()
        })
        
    except Exception as e:
        logger.error(f"RAG add documents error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rag/retrieve-context', methods=['POST'])
@limiter.limit("50 per hour")
def rag_retrieve_context():
    """Retrieve relevant context for a query"""
    try:
        data = request.json
        query = data.get('query', '').strip()
        top_k = data.get('top_k', 3)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Retrieve context using basic RAG
        context = basic_rag.retrieve_context(query, top_k)
        
        return jsonify({
            'success': True,
            'query': query,
            'context': context,
            'top_k': top_k
        })
        
    except Exception as e:
        logger.error(f"RAG retrieve context error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rag/stats', methods=['GET'])
def rag_stats():
    """Get RAG system statistics"""
    try:
        stats = basic_rag.get_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"RAG stats error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rag/clear', methods=['POST'])
@limiter.limit("5 per hour")
def rag_clear():
    """Clear all documents from RAG knowledge base"""
    try:
        basic_rag.clear_documents()
        
        return jsonify({
            'success': True,
            'message': 'All documents cleared successfully',
            'total_documents': basic_rag.get_document_count()
        })
        
    except Exception as e:
        logger.error(f"RAG clear error: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logger.error(f"Server error: {e}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(429)
def rate_limit_exceeded(e):
    """Handle rate limit errors"""
    return jsonify({
        'error': 'Rate limit exceeded. Please try again later.',
        'retry_after': e.description
    }), 429

if __name__ == '__main__':
    # Check environment
    environment = os.getenv('FLASK_ENV', 'development')
    logger.info(f"Starting app in {environment} mode")
    
    if environment == 'production':
        # Production settings
        socketio.run(
            app,
            host='0.0.0.0',
            port=int(os.getenv('PORT', 5000)),
            debug=False,
            allow_unsafe_werkzeug=True
        )
    else:
        # Development settings
        socketio.run(
            app,
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False,  # Set to False to avoid double initialization
            allow_unsafe_werkzeug=True
        )