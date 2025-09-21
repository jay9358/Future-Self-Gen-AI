# Session Management Service
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SessionService:
    """Service for managing user sessions and data persistence"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = timedelta(hours=24)  # 24 hours
    
    def create_session(self, user_data: Dict[str, Any] = None) -> str:
        """Create a new session"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "id": session_id,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "conversations": [],
            "user_data": user_data or {},
            "photo_path": None,
            "aged_avatars": {},
            "resume_data": None
        }
        logger.info(f"Created new session: {session_id}")
        return session_id
    
    def create_session_with_id(self, session_id: str, user_data: Dict[str, Any] = None) -> str:
        """Create a session with a specific ID"""
        self.sessions[session_id] = {
            "id": session_id,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "conversations": [],
            "user_data": user_data or {},
            "photo_path": None,
            "aged_avatars": {},
            "resume_data": None
        }
        logger.info(f"Created session with provided ID: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        if session_id in self.sessions:
            # Update last activity
            self.sessions[session_id]["last_activity"] = datetime.now().isoformat()
            return self.sessions[session_id]
        return None
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session data"""
        if session_id in self.sessions:
            self.sessions[session_id].update(updates)
            self.sessions[session_id]["last_activity"] = datetime.now().isoformat()
            return True
        return False
    
    def add_conversation(self, session_id: str, conversation: Dict[str, Any]) -> bool:
        """Add conversation to session"""
        if session_id in self.sessions:
            if "conversations" not in self.sessions[session_id]:
                self.sessions[session_id]["conversations"] = []
            self.sessions[session_id]["conversations"].append(conversation)
            self.sessions[session_id]["last_activity"] = datetime.now().isoformat()
            return True
        return False
    
    def update_conversation(self, session_id: str, conversation_id: str, updates: Dict[str, Any]) -> bool:
        """Update specific conversation"""
        if session_id in self.sessions:
            conversations = self.sessions[session_id].get("conversations", [])
            for conv in conversations:
                if conv.get("id") == conversation_id:
                    conv.update(updates)
                    self.sessions[session_id]["last_activity"] = datetime.now().isoformat()
                    return True
        return False
    
    def get_conversation(self, session_id: str, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get specific conversation"""
        if session_id in self.sessions:
            conversations = self.sessions[session_id].get("conversations", [])
            for conv in conversations:
                if conv.get("id") == conversation_id:
                    return conv
        return None
    
    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions"""
        now = datetime.now()
        expired_sessions = []
        
        for session_id, session_data in self.sessions.items():
            last_activity = datetime.fromisoformat(session_data["last_activity"])
            if now - last_activity > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        
        return len(expired_sessions)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        now = datetime.now()
        active_sessions = 0
        total_conversations = 0
        
        for session_data in self.sessions.values():
            last_activity = datetime.fromisoformat(session_data["last_activity"])
            if now - last_activity <= self.session_timeout:
                active_sessions += 1
                total_conversations += len(session_data.get("conversations", []))
        
        return {
            "total_sessions": len(self.sessions),
            "active_sessions": active_sessions,
            "total_conversations": total_conversations,
            "session_timeout_hours": self.session_timeout.total_seconds() / 3600
        }
    
    def export_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export session data for backup"""
        if session_id in self.sessions:
            session_data = self.sessions[session_id].copy()
            session_data["exported_at"] = datetime.now().isoformat()
            return session_data
        return None

# Global session service instance
session_service = SessionService()
