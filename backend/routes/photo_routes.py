# Photo Upload and Processing Routes
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import uuid
import os
from datetime import datetime
import logging

from config.settings import UPLOAD_FOLDER, AVATAR_FOLDER
from utils.file_utils import allowed_file
from services.session_service import session_service

logger = logging.getLogger(__name__)

photo_bp = Blueprint('photo', __name__, url_prefix='/api')

@photo_bp.route('/upload', methods=['POST'])
def upload_photo():
    """Handle photo upload"""
    try:
        if 'photo' not in request.files:
            return jsonify({"error": "No photo provided"}), 400
        
        file = request.files['photo']
        if not allowed_file(file.filename, ['png', 'jpg', 'jpeg', 'gif']):
            return jsonify({"error": "Invalid file type"}), 400
        
        # Generate unique filename
        filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        filepath = UPLOAD_FOLDER / filename
        file.save(str(filepath))
        
        # Create session using session service
        session_id = session_service.create_session({
            "photo_path": str(filepath)
        })
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "photo_url": f"/static/uploads/{filename}"
        })
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({"error": str(e)}), 500

@photo_bp.route('/age-photo', methods=['POST'])
def age_photo():
    """Generate aged version of uploaded photo"""
    try:
        data = request.json
        session_id = data.get('session_id')
        career = data.get('career')
        original_photo_url = data.get('original_photo_url')
        
        if not all([session_id, career, original_photo_url]):
            return jsonify({"error": "Missing required parameters"}), 400
        
        # For now, return original photo (AI aging can be implemented later)
        aged_url = original_photo_url
        
        # Update session with aged avatar
        session_service.update_session(session_id, {'aged_avatar': aged_url})
        
        return jsonify({
            "success": True,
            "aged_photo_url": aged_url
        })
        
    except Exception as e:
        logger.error(f"Age photo error: {e}")
        return jsonify({"error": str(e)}), 500
