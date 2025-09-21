# File utilities
import os
from pathlib import Path
from werkzeug.utils import secure_filename

def create_directories():
    """Create necessary directories if they don't exist"""
    from config.settings import UPLOAD_FOLDER, AVATAR_FOLDER, RESUME_FOLDER
    
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    AVATAR_FOLDER.mkdir(parents=True, exist_ok=True)
    RESUME_FOLDER.mkdir(parents=True, exist_ok=True)

def allowed_file(filename, extensions):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions

def get_title_for_year(career, year):
    """Get job title based on years of experience"""
    from models.career_database import CAREER_DATABASE
    
    progression = CAREER_DATABASE.get(career, {}).get('career_progression', {})
    
    for year_range, title in progression.items():
        if '-' in year_range:
            min_year, max_year = map(int, year_range.split('-'))
            if min_year <= year <= max_year:
                return title
        elif '+' in year_range:
            min_year = int(year_range.replace('+', ''))
            if year >= min_year:
                return title
    
    return "Professional"
