# Chat Service - Optimized for Speed and Performance
import asyncio
import logging
from typing import Optional, Dict, Any
from services.ai_services import (
    generate_response_async, 
    get_optimized_prompt, 
    is_ai_available,
    get_cache_stats,
    clear_cache
)
from services.rag_pipeline import rag_pipeline

logger = logging.getLogger(__name__)

class ChatService:
    """Optimized service for handling AI chat conversations with async processing"""
    
    def __init__(self):
        self.is_available = is_ai_available()
        self.response_cache = {}
        self.conversation_contexts = {}
    
    async def generate_future_self_response_async(self, career: str, question: str, context: Dict[str, Any]) -> str:
        """Generate response asynchronously with RAG-enhanced processing"""
        try:
            # Get enhanced context using RAG pipeline
            rag_context = rag_pipeline.get_relevant_context(career, question, context)
            
            # Generate enhanced prompt with RAG context
            prompt = rag_pipeline.generate_enhanced_prompt(career, question, rag_context)
            
            # Generate response asynchronously
            response = await generate_response_async(prompt, career, 'auto')
            
            
            self._update_conversation_context(career, question, response, context)
            
            return response
        
        except Exception as e:
            logger.error(f"Error in async response generation: {e}")
            return self._get_fallback_response(career, question)
    
    def generate_future_self_response(self, career: str, question: str, context: Dict[str, Any]) -> str:
        """Generate response with direct AI calls (ultra-simplified approach)"""
        logger.info(f"Generating response for career: {career}, question: {question[:50]}...")
        
        try:
            # Try direct AI call first (most reliable)
            response = self._generate_simple_response(career, question, context)
            if response and response.strip() and len(response) > 20:
                logger.info(f"Successfully generated AI response: {response[:100]}...")
                return response
        
            # If that fails, try a very simple approach
            logger.info("Simple response failed, trying ultra-simple approach...")
            response = self._generate_ultra_simple_response(career, question)
            if response and response.strip() and len(response) > 20:
                logger.info(f"Successfully generated ultra-simple response: {response[:100]}...")
                return response
        
            # If both fail, use fallback
            logger.warning("All AI approaches failed, using fallback response")
            return self._get_fallback_response(career, question)
            
        except Exception as e:
            logger.error(f"Error in response generation: {e}")
        return self._get_fallback_response(career, question)
    
    def _generate_ultra_simple_response(self, career: str, question: str) -> str:
        """Generate ultra-simple response with minimal processing"""
        try:
            from services.ai_services import get_gemini_model
            
            model = get_gemini_model('flash')
            if not model:
                return None
            
            # Ultra-simple prompt
            prompt = f"You are a {career.replace('_', ' ')} 10 years in the future. Answer: {question}"
            
            response = model.generate_content(prompt)
            if response and hasattr(response, 'text') and response.text:
                return response.text.strip()
            
            return None
        except Exception as e:
            logger.error(f"Ultra-simple response failed: {e}")
            return None
    
    def _try_async_approach(self, career: str, question: str, context: Dict[str, Any]) -> str:
        """Try async approach as fallback"""
        try:
            import threading
            import asyncio
            
            def run_async_in_thread():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(
                        self.generate_future_self_response_async(career, question, context)
                    )
                finally:
                    loop.close()
            
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_async_in_thread)
                return future.result(timeout=8)  # 8 second timeout
                
        except Exception as e:
            logger.error(f"Async approach failed: {e}")
            return self._get_fallback_response(career, question)
    
    def _is_fallback_response(self, response: str) -> bool:
        """Check if response is a generic fallback"""
        fallback_indicators = [
            "I remember asking myself that same question",
            "The industry has changed so much since I started",
            "That's a great question! The journey has been challenging",
            "Looking back, I can see how each decision led me"
        ]
        return any(indicator in response for indicator in fallback_indicators)
    
    def _generate_simple_response(self, career: str, question: str, context: Dict[str, Any]) -> str:
        """Generate a simple response without async processing as fallback"""
        try:
            from services.ai_services import get_gemini_model, get_claude_client
            from models.career_database import CAREER_DATABASE
            
            # Get career info for better context
            career_info = CAREER_DATABASE.get(career, {})
            career_title = career_info.get('title', career.replace('_', ' ').title())
            
            # Try Gemini first (usually faster)
            model = get_gemini_model('flash')
            if model:
                prompt = f"""You are {career_title} 10 years in the future. Be encouraging and specific.

Career: {career}
Question: {question}

Respond in first person as their future self. Be helpful and specific. Keep it under 150 words."""
                
                response = model.generate_content(prompt)
                if response and hasattr(response, 'text') and response.text:
                    response_text = response.text.strip()
                    if response_text and len(response_text) > 20:  # Ensure it's not too short
                        logger.info("Successfully generated response with Gemini")
                        return response_text
            
            # Try Claude as backup
            claude_client = get_claude_client()
            if claude_client:
                prompt = f"You are {career_title} 10 years in the future. Be specific and encouraging. Answer this question: {question}"
                response = claude_client.messages.create(
                    model="claude-3-5-sonnet-20241022",  # Latest Claude model
                    max_tokens=500,  # Increased for better responses
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}]
                )
                if response and response.content and response.content[0].text:
                    response_text = response.content[0].text.strip()
                    if response_text and len(response_text) > 20:
                        logger.info("Successfully generated response with Claude")
                        return response_text
                        
        except Exception as e:
            logger.error(f"Simple response generation failed: {e}")
        
        # Final fallback
        return self._get_fallback_response(career, question)
    
    def _update_conversation_context(self, career: str, question: str, response: str, context: Dict[str, Any]):
        """Update conversation context for better continuity"""
        session_id = context.get('session_id')
        if session_id:
            if session_id not in self.conversation_contexts:
                self.conversation_contexts[session_id] = {
                    'career': career,
                    'messages': [],
                    'topics_discussed': set()
                }
            
            # Store recent conversation
            self.conversation_contexts[session_id]['messages'].append({
                'question': question,
                'response': response,
                'timestamp': context.get('timestamp')
            })
            
            # Keep only last 10 messages for context
            if len(self.conversation_contexts[session_id]['messages']) > 10:
                self.conversation_contexts[session_id]['messages'] = \
                    self.conversation_contexts[session_id]['messages'][-10:]
    
    def get_conversation_context(self, session_id: str) -> Dict[str, Any]:
        """Get conversation context for a session"""
        return self.conversation_contexts.get(session_id, {})
    
    def clear_conversation_context(self, session_id: str):
        """Clear conversation context for a session"""
        if session_id in self.conversation_contexts:
            del self.conversation_contexts[session_id]
    
    def _get_fallback_response(self, career: str, question: str) -> str:
        """Get optimized fallback response using enhanced contextual system"""
        # Import the enhanced fallback function from app_structured
        try:
            import sys
            import os
            # Add the parent directory to the path to import from app_structured
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            
            from app_structured import generate_contextual_fallback_response
            return generate_contextual_fallback_response(career, question)
        except ImportError:
            # Fallback to simple responses if import fails
            career_titles = {
                'software_engineer': 'Software Engineer',
                'data_scientist': 'Data Scientist', 
                'doctor': 'Medical Doctor',
                'entrepreneur': 'Entrepreneur',
                'teacher': 'Teacher'
            }
            
            title = career_titles.get(career, career.replace('_', ' ').title())
            
            # Simple fallback responses
            fallback_responses = [
                f"Hello! I'm you from 10 years in the future as a successful {title}. The journey has been incredible - challenging but so rewarding. I've grown both personally and professionally. What would you like to know about our future?",
                f"Hey there! It's me, your future self, now a {title}. I remember being where you are now. The path wasn't always clear, but every step led to amazing opportunities. Ask me anything!",
                f"Hi! I'm you 10 years from now, working as a {title}. The transformation has been remarkable. I've learned so much and achieved things I never thought possible. What's on your mind?"
            ]
            
            # Use question hash for consistent responses
            question_hash = hash(question) % len(fallback_responses)
            return fallback_responses[question_hash]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            'ai_available': self.is_available,
            'active_conversations': len(self.conversation_contexts),
            'cache_stats': get_cache_stats(),
            'total_messages': sum(
                len(ctx['messages']) for ctx in self.conversation_contexts.values()
            )
        }
    
    def clear_all_caches(self):
        """Clear all caches and contexts"""
        clear_cache()
        self.conversation_contexts.clear()
        logger.info("All caches and contexts cleared")

# Global instance
chat_service = ChatService()
