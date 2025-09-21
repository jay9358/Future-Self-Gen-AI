# Career Analysis and Skills Routes
from flask import Blueprint, request, jsonify
import logging
from datetime import datetime

from models.career_database import CAREER_DATABASE
from services.resume_analyzer import calculate_career_match, generate_learning_roadmap
from services.ai_services import get_gemini_model

logger = logging.getLogger(__name__)

career_bp = Blueprint('career', __name__, url_prefix='/api')

@career_bp.route('/skills-analysis', methods=['POST'])
def skills_analysis():
    """Analyze skills gap for career transition"""
    try:
        data = request.json
        session_id = data.get('session_id')
        target_career = data.get('career')
        current_skills = data.get('current_skills', [])
        
        if not target_career:
            return jsonify({"error": "Career not specified"}), 400
        
        # Calculate match
        career_info = CAREER_DATABASE.get(target_career, {})
        required_skills = career_info.get('required_skills', [])
        match_result = calculate_career_match(current_skills, required_skills)
        
        # Generate learning path
        learning_path = generate_learning_roadmap(
            match_result['missing_skills'],
            target_career
        )
        
        return jsonify({
            "success": True,
            "match_result": match_result,
            "learning_path": learning_path,
            "career_info": {
                "title": career_info.get("title"),
                "salary_range": career_info.get("salary_range"),
                "career_progression": career_info.get("career_progression")
            }
        })
        
    except Exception as e:
        logger.error(f"Skills analysis error: {e}")
        return jsonify({"error": str(e)}), 500

@career_bp.route('/generate-timeline', methods=['POST'])
def generate_timeline():
    """Generate career timeline projection"""
    try:
        data = request.json
        career = data.get('career')
        
        if not career:
            return jsonify({"error": "Career not specified"}), 400
        
        career_info = CAREER_DATABASE.get(career, {})
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
        
        return jsonify({
            "success": True,
            "timeline": timeline
        })
        
    except Exception as e:
        logger.error(f"Timeline generation error: {e}")
        return jsonify({"error": str(e)}), 500

@career_bp.route('/generate-projects', methods=['POST'])
def generate_projects():
    """Generate project ideas for career development"""
    try:
        data = request.json
        career = data.get('career')
        skill_level = data.get('skill_level', 'beginner')
        
        if not career:
            return jsonify({"error": "Career not specified"}), 400
        
        career_info = CAREER_DATABASE.get(career, {})
        
        # Generate project ideas based on career and skill level
        projects = {
            "beginner": [
                {
                    "title": f"Basic {career_info.get('title', career)} Portfolio",
                    "description": f"Create a simple portfolio showcasing your {career} skills",
                    "duration": "2-4 weeks",
                    "skills_learned": career_info.get('core_skills', [])[:3]
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

@career_bp.route('/interview-prep', methods=['POST'])
def interview_prep():
    """Generate interview preparation materials"""
    try:
        data = request.json
        career = data.get('career')
        experience_level = data.get('experience_level', 'entry')
        
        if not career:
            return jsonify({"error": "Career not specified"}), 400
        
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

@career_bp.route('/salary-projection', methods=['POST'])
def salary_projection():
    """Generate salary projection for career path"""
    try:
        data = request.json
        career = data.get('career')
        current_experience = data.get('current_experience', 0)
        location = data.get('location', 'US')
        
        if not career:
            return jsonify({"error": "Career not specified"}), 400
        
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
