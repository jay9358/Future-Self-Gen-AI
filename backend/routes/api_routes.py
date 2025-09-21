# Main API Routes - Aggregates all route modules
from flask import Blueprint, request, jsonify
from datetime import datetime
import uuid
import os
from werkzeug.utils import secure_filename
from services.resume_analyzer import extract_skills_from_resume, calculate_career_match, generate_learning_roadmap, extract_text_from_pdf, extract_text_from_docx
from services.ai_services import get_gemini_model
from models.career_database import CAREER_DATABASE
from config.settings import RESUME_EXTENSIONS, UPLOAD_FOLDER, AVATAR_FOLDER, RESUME_FOLDER

# Import route modules
from routes.photo_routes import photo_bp
from routes.chat_routes import chat_bp
from routes.career_routes import career_bp
from services.session_service import session_service

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Register sub-blueprints
api_bp.register_blueprint(photo_bp)
api_bp.register_blueprint(chat_bp)
api_bp.register_blueprint(career_bp)

def allowed_file(filename, extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions

@api_bp.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "platform": os.name,
        "timestamp": datetime.now().isoformat(),
        "features": ["resume_analysis", "skills_matching", "career_roadmap"]
    })

@api_bp.route('/create-session', methods=['POST'])
def create_session():
    """Create a new session"""
    try:
        data = request.json or {}
        user_data = data.get('user_data', {})
        session_id = session_service.create_session(user_data)
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "message": "Session created successfully"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/upload-resume', methods=['POST'])
def upload_resume():
    """Handle resume upload and analysis"""
    try:
        if 'resume' not in request.files:
            return jsonify({"error": "No resume provided"}), 400
        
        file = request.files['resume']
        session_id = request.form.get('session_id')
        
        session = session_service.get_session(session_id) if session_id else None
        if not session:
            session_id = session_service.create_session()
        
        if file and allowed_file(file.filename, RESUME_EXTENSIONS):
            filename = f"{session_id}_resume_{secure_filename(file.filename)}"
            filepath = RESUME_FOLDER / filename
            file.save(str(filepath))
            
            # Extract text based on file type
            file_ext = filename.rsplit('.', 1)[1].lower()
            if file_ext == 'pdf':
                resume_text = extract_text_from_pdf(filepath)
            elif file_ext == 'docx':
                resume_text = extract_text_from_docx(filepath)
            else:
                with open(filepath, 'r', encoding='utf-8') as f:
                    resume_text = f.read()
            
            # Extract skills and information
            extracted_info = extract_skills_from_resume(resume_text)
            
            # Use AI to analyze resume
            gemini_model = get_gemini_model()
            if gemini_model:
                try:
                    prompt = f"""Analyze this resume and extract:
                    1. Current job title/role
                    2. Key skills (technical and soft)
                    3. Years of experience
                    4. Education level
                    5. Industry experience
                    6. Career goals (if mentioned)
                    
                    Resume:
                    {resume_text[:2000]}
                    
                    Return as JSON format."""
                    
                    response = gemini_model.generate_content(prompt)
                    ai_analysis = response.text
                except:
                    ai_analysis = None
            else:
                ai_analysis = None
            
            # Store resume data in session
            session_service.update_session(session_id, {
                'resume_data': {
                    "filepath": str(filepath),
                    "extracted_info": extracted_info,
                    "ai_analysis": ai_analysis,
                    "resume_text": resume_text[:500]  # Store snippet
                }
            })
            
            # Calculate career matches
            career_matches = {}
            for career_key, career_info in CAREER_DATABASE.items():
                match_result = calculate_career_match(
                    extracted_info["skills"],
                    career_info.get("required_skills", [])
                )
                career_matches[career_key] = match_result
            
            # Sort careers by match percentage
            sorted_careers = sorted(
                career_matches.items(),
                key=lambda x: x[1]["match_percentage"],
                reverse=True
            )
            
            return jsonify({
                "success": True,
                "session_id": session_id,
                "extracted_info": extracted_info,
                "career_matches": dict(sorted_careers[:5]),  # Top 5 matches
                "ai_analysis": ai_analysis
            })
            
    except Exception as e:
        print(f"Resume upload error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/skills-gap-analysis', methods=['POST'])
def skills_gap_analysis():
    """Analyze skills gap for a specific career"""
    try:
        data = request.json
        session_id = data.get('session_id')
        target_career = data.get('career')
        
        session = session_service.get_session(session_id)
        if not session:
            return jsonify({"error": "Invalid session"}), 400
        
        resume_data = session.get('resume_data', {})
        user_skills = resume_data.get('extracted_info', {}).get('skills', [])
        
        career_info = CAREER_DATABASE.get(target_career, {})
        required_skills = career_info.get('required_skills', [])
        
        # Calculate gap
        match_result = calculate_career_match(user_skills, required_skills)
        
        # Generate learning roadmap
        roadmap = generate_learning_roadmap(
            match_result['missing_skills'],
            target_career
        )
        
        # Estimate time to career readiness
        total_missing = len(match_result['missing_skills'])
        estimated_months = total_missing * 2  # Rough estimate: 2 months per skill
        
        # Generate personalized advice using AI
        advice = ""
        gemini_model = get_gemini_model()
        if gemini_model:
            try:
                prompt = f"""Given a person with skills: {', '.join(user_skills)},
                who wants to become a {target_career},
                and needs to learn: {', '.join(match_result['missing_skills'][:5])},
                provide 3 specific action steps they should take in the next month.
                Be practical and specific."""
                
                response = gemini_model.generate_content(prompt)
                advice = response.text
            except:
                advice = "Focus on building the fundamental skills first."
        
        return jsonify({
            "success": True,
            "match_result": match_result,
            "learning_roadmap": roadmap,
            "estimated_time_months": estimated_months,
            "personalized_advice": advice,
            "career_info": {
                "title": career_info.get("title"),
                "salary_range": career_info.get("salary_range"),
                "career_progression": career_info.get("career_progression")
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add other API routes here...
