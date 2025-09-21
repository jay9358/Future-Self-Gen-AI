# Chat and Conversation Routes
from flask import Blueprint, request, jsonify
import uuid
from datetime import datetime
import logging
import json

from models.career_database import CAREER_DATABASE
from services.chat_service import chat_service
from services.session_service import session_service

logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__, url_prefix='/api')

@chat_bp.route('/start-conversation', methods=['POST'])
def start_conversation():
    """Start conversation with future self"""
    try:
        data = request.json
        session_id = data.get('session_id')
        career = data.get('career')
        name = data.get('name', 'Friend')
        
        session = session_service.get_session(session_id)
        if not session:
            return jsonify({"error": "Invalid session"}), 400
        
        conversation_id = str(uuid.uuid4())
        career_info = CAREER_DATABASE.get(career, {})
        
        # Generate personalized greeting
        greeting = chat_service.generate_future_self_response(
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
        
        session_service.add_conversation(session_id, conversation)
        
        return jsonify({
            "success": True,
            "conversation_id": conversation_id,
            "greeting": greeting
        })
        
    except Exception as e:
        logger.error(f"Start conversation error: {e}")
        return jsonify({"error": str(e)}), 500

