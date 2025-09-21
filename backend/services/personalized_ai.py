# personalized_ai.py - Enhanced with Google Gemini Free Tier and proper dotenv
import os
import sys
import json
import logging
import random
from typing import Optional, Dict, Any, List
from pathlib import Path
import hashlib
import time
from datetime import datetime
from collections import defaultdict

# Load environment variables FIRST before anything else
from dotenv import load_dotenv

# Try multiple paths to find .env file
def load_environment():
    """Load environment variables from .env file"""
    # Try different paths where .env might be
    possible_paths = [
        Path('.env'),  # Current directory
        Path(__file__).resolve().parent / '.env',  # Same dir as this file
        Path(__file__).resolve().parent.parent / '.env',  # Parent directory (backend/)
        Path(__file__).resolve().parent.parent.parent / '.env',  # Root project directory
    ]
    
    for env_path in possible_paths:
        if env_path.exists():
            load_dotenv(env_path)
            print(f"✅ Loaded environment from: {env_path}")
            # Verify key is loaded
            if os.getenv('GEMINI_API_KEY'):
                print("✅ GEMINI_API_KEY found in environment")
            else:
                print("⚠️ GEMINI_API_KEY not found in environment")
            return True
    
    print("⚠️ No .env file found. Tried these locations:")
    for path in possible_paths:
        print(f"  - {path.absolute()}")
    return False

# Load environment on module import
load_environment()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PersonalizedAIService:
    """Emotionally intelligent AI using Google Gemini free tier"""
    
    def __init__(self):
        self.gemini_model = None
        self.gemini_available = False
        self.personas = {}
        self.conversation_memory = {}
        
        # Enhanced memory systems
        self.response_history = defaultdict(list)
        self.emotional_state = defaultdict(dict)
        self.topic_progression = defaultdict(list)
        self.relationship_depth = defaultdict(int)
        
        # Rate limiting for free tier
        self.last_api_call = 0
        self.api_call_count = 0
        self.rate_limit_per_minute = 15  # Gemini free tier limit
        
        # Initialize Gemini
        self.initialize_gemini()
    
    def initialize_gemini(self) -> bool:
        """Initialize Google Gemini API (free tier)"""
        try:
            # Try importing the library
            try:
                import google.generativeai as genai
            except ImportError:
                logger.warning("google-generativeai not installed")
                logger.info("Install with: pip install google-generativeai")
                self.gemini_available = False
                return False
            
            # Try multiple ways to get the API key
            api_key = None
            
            # Method 1: Direct environment variable
            api_key = os.getenv('GEMINI_API_KEY')
            
            # Method 2: Try uppercase
            if not api_key:
                api_key = os.getenv('GEMINI_API_KEY')
            
            # Method 3: Try from os.environ directly
            if not api_key:
                api_key = os.environ.get('GEMINI_API_KEY')
            
            # Method 4: Try loading .env again
            if not api_key:
                from dotenv import load_dotenv, find_dotenv
                load_dotenv(find_dotenv())
                api_key = os.getenv('GEMINI_API_KEY')
            
            if not api_key:
                logger.warning("GEMINI_API_KEY not found in environment variables")
                logger.info("Please add to .env file: GEMINI_API_KEY=your_key_here")
                logger.info("Get your free API key from: https://makersuite.google.com/app/apikey")
                
                # Create a sample .env file if it doesn't exist
                sample_env_path = Path('.env.example')
                if not sample_env_path.exists():
                    with open(sample_env_path, 'w') as f:
                        f.write("# Google Gemini API Key (free tier)\n")
                        f.write("GEMINI_API_KEY=your_api_key_here\n")
                    logger.info(f"Created sample .env.example file at: {sample_env_path.absolute()}")
                
                self.gemini_available = False
                return False
            
            logger.info(f"API key found: {api_key[:10]}...")  # Show first 10 chars for verification
            
            # Configure Gemini
            genai.configure(api_key=api_key)
            
            # Use gemini-pro (free tier model)
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
            
            # Test the connection
            try:
                test_response = self.gemini_model.generate_content("Say 'test successful'")
                if test_response and test_response.text:
                    logger.info(f"✅ Gemini API connected successfully (free tier)")
                    logger.info(f"Test response: {test_response.text[:50]}")
                    self.gemini_available = True
                    return True
                else:
                    logger.warning("Gemini test returned empty response")
                    self.gemini_available = False
                    return False
            except Exception as e:
                logger.warning(f"Gemini API test failed: {e}")
                if "API_KEY_INVALID" in str(e):
                    logger.error("Invalid API key! Please check your GEMINI_API_KEY")
                elif "QUOTA" in str(e).upper():
                    logger.warning("API quota exceeded. Will use fallback responses.")
                self.gemini_available = False
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self.gemini_available = False
            return False
    
    def generate_response(self, 
                         message: str, 
                         persona: Dict[str, Any], 
                         session_id: str = None,
                         conversation_history: List[Dict] = None) -> str:
        """Generate response using Gemini or fallback"""
        
        # Validate inputs
        if not message:
            message = "Hello"
        if not persona:
            persona = self._create_default_persona()
        if not session_id:
            session_id = "default"
        
        try:
            # Update conversation state
            self._update_conversation_state(session_id, message, conversation_history)
            
            # Analyze context
            context = self._analyze_deep_context(message, conversation_history, session_id)
            
            # Check for critical situations
            if self._is_crisis(context):
                return self._generate_crisis_response(persona, context)
            
            # Try Gemini if available and not rate limited
            if self.gemini_available and self._can_use_api():
                try:
                    gemini_response = self._generate_with_gemini(
                        message, persona, context, session_id, conversation_history
                    )
                    if gemini_response:
                        self._record_response(session_id, gemini_response, context)
                        return gemini_response
                except Exception as e:
                    logger.warning(f"Gemini generation failed, using fallback: {e}")
            
            # Fallback to structured response
            response = self._generate_structured_response(message, persona, context, session_id)
            self._record_response(session_id, response, context)
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._generate_emergency_fallback(persona)
    
    def _can_use_api(self) -> bool:
        """Check if we can make an API call (rate limiting)"""
        current_time = time.time()
        
        # Reset counter if a minute has passed
        if current_time - self.last_api_call > 60:
            self.api_call_count = 0
        
        # Check if under rate limit
        if self.api_call_count < self.rate_limit_per_minute:
            return True
        
        logger.info("Rate limit reached, using fallback")
        return False
    
    def _generate_with_gemini(self, message: str, persona: Dict[str, Any], 
                            context: Dict[str, Any], session_id: str,
                            conversation_history: List[Dict] = None) -> Optional[str]:
        """Generate response using Gemini API"""
        
        if not self.gemini_model:
            return None
        
        try:
            # Build prompt for Gemini
            prompt = self._build_gemini_prompt(message, persona, context, conversation_history)
            
            # Generate response with safety settings
            response = self.gemini_model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.8,
                    'top_p': 0.9,
                    'max_output_tokens': 300,
                    'stop_sequences': ["Past self:", "User:", "Human:"]
                },
                safety_settings={
                    'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                    'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                    'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                    'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE'
                }
            )
            
            # Update rate limiting
            self.last_api_call = time.time()
            self.api_call_count += 1
            
            # Extract and validate response
            if response and response.text:
                generated_text = response.text.strip()
                
                # Validate it's in character
                if self._validate_gemini_response(generated_text):
                    logger.info("Generated response using Gemini")
                    return generated_text
                else:
                    logger.warning("Gemini response failed validation, using fallback")
                    return None
            
            return None
            
        except Exception as e:
            error_str = str(e)
            logger.error(f"Gemini generation error: {error_str}")
            
            # Handle specific errors
            if "quota" in error_str.lower():
                logger.warning("Gemini quota exceeded, disabling temporarily")
                self.gemini_available = False
            elif "api_key" in error_str.lower():
                logger.error("API key issue detected")
                self.gemini_available = False
            
            return None
    
    def _build_gemini_prompt(self, message: str, persona: Dict[str, Any], 
                           context: Dict[str, Any], 
                           conversation_history: List[Dict] = None) -> str:
        """Build effective prompt for Gemini"""
        
        name = persona.get('name', 'Friend')
        role = persona.get('current_role', 'Professional')
        age = persona.get('current_age', 35)
        past_age = persona.get('past_age', 25)
        
        # Get relevant persona details
        achievements = persona.get('achievements', [])
        memories = persona.get('specific_memories', [])
        wisdom = persona.get('wisdom_gained', [])
        challenges = persona.get('challenges_overcome', [])
        
        # Get context
        emotion = context.get('emotional_state', 'neutral')
        depth = context.get('depth', 0)
        
        prompt = f"""You are {name}, speaking from 10 years in the future. You are now {age} years old and work as a {role}.

IMPORTANT: You ARE their future self. Speak in first person about YOUR journey. Never break character.

Your journey:
- At age {past_age}, you struggled with: {', '.join(challenges[:3])}
- You achieved: {', '.join(achievements[:2])}
- Specific memories: {', '.join(memories[:2])}
- Wisdom gained: {random.choice(wisdom)}

Their current emotional state: {emotion}

Their message: "{message}"

Respond as their future self with:
1. Acknowledge their emotion
2. Share a specific memory from your journey
3. Offer wisdom from lived experience
4. Ask a deepening question

Keep it under 150 words. Be warm, authentic, and vulnerable.

Your response:"""
        
        return prompt
    
    def _validate_gemini_response(self, response: str) -> bool:
        """Validate that Gemini response stays in character"""
        
        if not response or len(response) < 20:
            return False
        
        # Check for breaking character
        forbidden_phrases = [
            "as an ai", "language model", "assistant",
            "i cannot", "i don't have personal",
            "my programming", "i was created"
        ]
        
        response_lower = response.lower()
        
        for phrase in forbidden_phrases:
            if phrase in response_lower:
                return False
        
        return True
    
    def _update_conversation_state(self, session_id: str, message: str, 
                                  conversation_history: List[Dict] = None):
        """Update conversation metrics"""
        
        self.relationship_depth[session_id] += 1
        
        # Track emotional state
        current_emotion = self._detect_emotion(message)
        
        if session_id not in self.emotional_state:
            self.emotional_state[session_id] = {
                'current': current_emotion,
                'history': [current_emotion],
                'trajectory': 'neutral'
            }
        else:
            self.emotional_state[session_id]['history'].append(current_emotion)
            self.emotional_state[session_id]['current'] = current_emotion
            self.emotional_state[session_id]['trajectory'] = self._calculate_trajectory(
                self.emotional_state[session_id]['history']
            )
    
    def _detect_emotion(self, message: str) -> str:
        """Detect primary emotion"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hopeless', 'give up', 'desperate']):
            return 'hopeless'
        elif any(word in message_lower for word in ['worried', 'scared', 'anxious']):
            return 'anxious'
        elif any(word in message_lower for word in ['sad', 'depressed', 'down']):
            return 'sad'
        elif any(word in message_lower for word in ['happy', 'excited', 'great']):
            return 'happy'
        elif any(word in message_lower for word in ['confused', 'lost', "don't know"]):
            return 'confused'
        elif any(word in message_lower for word in ['hi', 'hey', 'hello']):
            return 'greeting'
        else:
            return 'neutral'
    
    def _calculate_trajectory(self, history: List[str]) -> str:
        """Calculate emotional trajectory"""
        if len(history) < 2:
            return 'stable'
        
        recent = history[-3:] if len(history) >= 3 else history
        
        positive = ['happy', 'excited', 'grateful', 'determined']
        negative = ['hopeless', 'anxious', 'sad', 'frustrated']
        
        pos_count = sum(1 for e in recent if e in positive)
        neg_count = sum(1 for e in recent if e in negative)
        
        if pos_count > neg_count:
            return 'improving'
        elif neg_count > pos_count:
            return 'struggling'
        else:
            return 'stable'
    
    def _analyze_deep_context(self, message: str, conversation_history: List[Dict], 
                            session_id: str) -> Dict[str, Any]:
        """Analyze conversation context"""
        
        message_lower = message.lower()
        depth = self.relationship_depth[session_id]
        emotional_state = self.emotional_state.get(session_id, {})
        
        return {
            'depth': depth,
            'emotional_state': emotional_state.get('current', 'neutral'),
            'trajectory': emotional_state.get('trajectory', 'stable'),
            'is_crisis': self._is_crisis_message(message_lower),
            'is_greeting': self._is_greeting(message_lower),
            'is_question': '?' in message,
            'message_lower': message_lower
        }
    
    def _is_crisis_message(self, message: str) -> bool:
        """Detect crisis situations"""
        crisis_indicators = [
            'want to die', 'kill myself', 'end it all',
            'no point', 'give up', 'hopeless',
            'can\'t go on', 'not worth it'
        ]
        return any(indicator in message for indicator in crisis_indicators)
    
    def _is_crisis(self, context: Dict[str, Any]) -> bool:
        """Check if context indicates crisis"""
        return (context.get('is_crisis', False) or 
                (context.get('emotional_state') == 'hopeless' and 
                 context.get('trajectory') == 'struggling'))
    
    def _is_greeting(self, message: str) -> bool:
        """Check if message is greeting"""
        greetings = ['hi', 'hey', 'hello', 'howdy', 'greetings']
        message_clean = message.strip().lower()
        return any(message_clean == g or message_clean.startswith(g + ' ') for g in greetings)
    
    def _generate_crisis_response(self, persona: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate crisis support response"""
        
        name = persona.get('name', 'Friend')
        role = persona.get('current_role', 'Professional')
        
        return f"""{name}, I need you to hear this: You matter. You survive this. 

I'm here, 10 years later, as a {role}. The darkness you're in right now? I lived through it. It felt endless, but it wasn't.

Please reach someone today:
- National Suicide Prevention Lifeline: 988
- Crisis Text Line: Text HOME to 741741
- Or call emergency services: 911

I'm proof that staying alive is worth it. The pain is temporary, but the choice to keep going changes everything."""
    
    def _generate_structured_response(self, message: str, persona: Dict[str, Any], 
                                     context: Dict[str, Any], session_id: str) -> str:
        """Generate structured fallback response"""
        
        name = persona.get('name', 'Friend')
        role = persona.get('current_role', 'Professional')
        
        # Get persona elements
        achievements = persona.get('achievements', ['built my career'])
        memories = persona.get('specific_memories', ['the journey'])
        wisdom = persona.get('wisdom_gained', ['persistence is key'])
        challenges = persona.get('challenges_overcome', ['self-doubt'])
        
        # Avoid repetition by tracking what we've said
        used_items = self.response_history.get(session_id, [])
        
        # Filter out used elements
        available_achievements = [a for a in achievements if not any(a in r for r in used_items[-3:])]
        available_memories = [m for m in memories if not any(m in r for r in used_items[-3:])]
        available_wisdom = [w for w in wisdom if not any(w in r for r in used_items[-3:])]
        
        achievement = random.choice(available_achievements if available_achievements else achievements)
        memory = random.choice(available_memories if available_memories else memories)
        wisdom_point = random.choice(available_wisdom if available_wisdom else wisdom)
        challenge = random.choice(challenges)
        
        emotion = context.get('emotional_state', 'neutral')
        depth = context.get('depth', 0)
        
        if context.get('is_greeting'):
            if depth <= 1:
                responses = [
                    f"Hey {name}! This is surreal - talking to you from 10 years in the future. I'm now a {role}. I remember being exactly where you are, full of questions and uncertainty. The journey ahead is incredible. What's on your mind?",
                    f"{name}, it's me - you from 2035. I'm a {role} now, living proof that everything works out. I have so much to tell you about what's coming. Where should we start?",
                    f"Hello {name}. Your future self here, now a {role}. I've been waiting to talk to you. The path between where you are and where I am is wild but worth every step. What do you need to know?"
                ]
            else:
                responses = [
                    f"Hey again {name}. Still here, still your future self. What's coming up for you now?",
                    f"{name}, good to continue our conversation. How are you processing everything we've talked about?",
                    f"Hi {name}. Each time we talk, I see you getting closer to who I am now. What's on your heart?"
                ]
            return random.choice(responses)
        
        elif emotion in ['anxious', 'confused', 'sad']:
            return f"{name}, I hear the weight in your words. I remember {memory} - feeling exactly like you do now. I struggled with {challenge} for what felt like forever. But here's what I learned: {wisdom_point}. As a {role} now, I promise you this feeling is temporary. What specific part feels overwhelming?"
        
        elif emotion == 'happy':
            return f"I love your energy, {name}! That enthusiasm? It's what carried me through everything. I've {achievement} as a {role}, and it started with moments exactly like this. {wisdom_point}. How can we build on this momentum?"
        
        else:
            if depth > 5:
                return f"{name}, we've been talking for a while now. I can see the shift happening - you're not the same person who started this conversation. As a {role} who's {achievement}, I recognize transformation when I see it. You're closer than you think."
            else:
                return f"{name}, from my position as a {role}, I see how {memory} was actually preparing me for {achievement}. The key: {wisdom_point}. Trust the process - every step matters, even when the path isn't clear. What resonates most with you?"
    
    def _record_response(self, session_id: str, response: str, context: Dict[str, Any]):
        """Record response to prevent repetition"""
        self.response_history[session_id].append(response)
        
        # Keep only last 20 responses
        if len(self.response_history[session_id]) > 20:
            self.response_history[session_id] = self.response_history[session_id][-20:]
    
    def _generate_emergency_fallback(self, persona: Dict[str, Any]) -> str:
        """Emergency fallback"""
        name = persona.get('name', 'Friend')
        role = persona.get('current_role', 'Professional')
        
        return f"Hey {name}, your future self here - now a {role}. Technical hiccup, but I'm still here. The journey from where you are to where I am is worth every challenge. What do you need to hear right now?"
    
    def _create_default_persona(self) -> Dict[str, Any]:
        """Create default persona"""
        return {
            'name': 'Friend',
            'current_age': 35,
            'past_age': 25,
            'current_role': 'Successful Professional',
            'career_path': 'professional',
            'achievements': [
                'Built a meaningful career',
                'Found work-life balance',
                'Made lasting impact'
            ],
            'challenges_overcome': [
                'job search struggles',
                'imposter syndrome',
                'self-doubt'
            ],
            'specific_memories': [
                'those sleepless nights',
                'the first breakthrough',
                'when everything clicked'
            ],
            'wisdom_gained': [
                'consistency beats perfection',
                'failure is just data',
                'small steps compound'
            ]
        }
    
    def create_future_self_persona(self, user_data: Dict[str, Any], career_goal: str) -> Dict[str, Any]:
        """Create persona from user data"""
        
        personal_info = user_data.get('personal_info', {})
        name = personal_info.get('name', 'Friend')
        
        if not name or len(name) < 2:
            name = 'Friend'
        
        return {
            'name': name,
            'current_age': user_data.get('age', 25) + 10,
            'past_age': user_data.get('age', 25),
            'current_role': self._enhance_role_title(career_goal, user_data.get('years_experience', 0) + 10),
            'career_path': career_goal,
            'achievements': [
                'Built successful products',
                'Led amazing teams',
                'Found work-life balance',
                'Made lasting impact',
                'Became industry expert'
            ],
            'challenges_overcome': [
                'months of rejections',
                'imposter syndrome',
                'skill gaps',
                'burnout',
                'career pivots'
            ],
            'specific_memories': [
                'application #73 getting rejected',
                'crying after failed interviews',
                'the email that changed everything',
                'first day at dream job',
                'moment I knew I made it'
            ],
            'wisdom_gained': [
                'rejection is redirection',
                'progress over perfection',
                'network beats resume',
                'consistency compounds',
                'failure teaches fastest'
            ]
        }
    
    def _enhance_role_title(self, career: str, years: int) -> str:
        """Generate role title"""
        prefix = "Senior" if years > 5 else ""
        titles = {
            'software_engineer': 'Software Engineer',
            'data_scientist': 'Data Scientist',
            'product_manager': 'Product Manager'
        }
        base = titles.get(career, career.replace('_', ' ').title())
        return f"{prefix} {base}".strip() if prefix else base
    
    def is_model_available(self) -> bool:
        """Check if response generation available"""
        return True  # Always true due to fallback

# Create global instance
personalized_ai_service = PersonalizedAIService()

# Export
__all__ = ['PersonalizedAIService', 'personalized_ai_service']