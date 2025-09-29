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
        
        # Rate limiting for free tier - very generous for Gemini-only mode
        self.last_api_call = 0
        self.api_call_count = 0
        self.rate_limit_per_minute = 120  # Very generous limit for Gemini-only
        
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
            
            # Try to find a working model
            model_names_to_try = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-pro']
            
            for model_name in model_names_to_try:
                try:
                    self.gemini_model = genai.GenerativeModel(model_name)
                    logger.info(f"✅ Using {model_name} for chat responses")
                    break
                except Exception as e:
                    logger.warning(f"Failed to initialize {model_name}: {e}")
                    continue
            
            if not self.gemini_model:
                logger.error("No working Gemini model found for chat")
                self.gemini_available = False
                return False
            
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
            
            # Force Gemini-only responses - no fallbacks
            if not self.gemini_available:
                logger.error("❌ Gemini not available - no response generated")
                return None
            
            if not self._can_use_api():
                logger.warning("❌ Rate limit reached - no response generated")
                return None
            
            logger.info(f"🚀 Generating Gemini response for session {session_id}")
            try:
                gemini_response = self._generate_with_gemini(
                    message, persona, context, session_id, conversation_history
                )
                if gemini_response:
                    logger.info("✅ Successfully generated response using Gemini")
                    self._record_response(session_id, gemini_response, context)
                    return gemini_response
                else:
                    logger.error("❌ Gemini returned no response - no fallback")
                    return None
            except Exception as e:
                logger.error(f"❌ Gemini generation failed: {e} - no fallback")
                return None
            
        except Exception as e:
            logger.error(f"Error generating response: {e} - no fallback")
            return None
    
    def _can_use_api(self) -> bool:
        """Check if we can make an API call (rate limiting)"""
        current_time = time.time()
        
        # Reset counter if a minute has passed
        if current_time - self.last_api_call > 60:
            self.api_call_count = 0
        
        # Check if under rate limit - very generous for Gemini-only mode
        if self.api_call_count < self.rate_limit_per_minute:
            return True
        
        # If we're close to limit, still allow many more calls
        if self.api_call_count < self.rate_limit_per_minute + 50:
            logger.info(f"Near rate limit ({self.api_call_count}/{self.rate_limit_per_minute}), but allowing call")
            return True
        
        logger.warning("Rate limit reached - waiting for reset")
        return False
    
    def _generate_with_gemini(self, message: str, persona: Dict[str, Any], 
                            context: Dict[str, Any], session_id: str,
                            conversation_history: List[Dict] = None) -> Optional[str]:
        """Generate response using Gemini API"""
        
        if not self.gemini_model:
            logger.warning("Gemini model not available")
            return None
        
        try:
            # Build prompt for Gemini
            prompt = self._build_gemini_prompt(message, persona, context, conversation_history)
            logger.info(f"Generating Gemini response for session {session_id}")
            
            # Generate response with safety settings
            response = self.gemini_model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.9,  # Higher temperature for more creative, natural responses
                    'top_p': 0.95,       # Higher top_p for more diverse vocabulary
                    'max_output_tokens': 200,  # Shorter responses for more natural conversation
                    'stop_sequences': ["Past self:", "User:", "Human:", "Assistant:", "AI:"]
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
                logger.info(f"Gemini generated response: {generated_text[:100]}...")
                
                # Post-process to make more natural
                processed_text = self._post_process_response(generated_text)
                
                # Validate it's in character
                if self._validate_gemini_response(processed_text):
                    logger.info("✅ Gemini response validated successfully")
                    return processed_text
                else:
                    logger.warning("Gemini response failed validation, using fallback")
                    return None
            else:
                logger.warning("Gemini returned empty response")
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
            elif "safety" in error_str.lower():
                logger.warning("Gemini safety filter triggered, trying with different settings")
                # Try again with more permissive settings
                try:
                    response = self.gemini_model.generate_content(
                        prompt,
                        generation_config={
                            'temperature': 0.7,
                            'max_output_tokens': 200
                        }
                    )
                    if response and response.text:
                        return response.text.strip()
                except:
                    pass
            
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
        
        # Build conversation context
        conversation_context = ""
        if conversation_history and len(conversation_history) > 0:
            recent_messages = conversation_history[-4:]  # Last 4 messages for context
            conversation_context = "\n\nRECENT CONVERSATION:\n"
            for msg in recent_messages:
                role_label = "You (past)" if msg.get('role') == 'user' else "Me (future)"
                conversation_context += f"{role_label}: {msg.get('content', '')}\n"
        
        # Avoid repetition by checking what we've already discussed
        used_topics = []
        used_phrases = []
        if conversation_history:
            for msg in conversation_history[-8:]:  # Check last 8 messages
                if msg.get('role') == 'assistant':
                    content = msg.get('content', '').lower()
                    # Track specific phrases to avoid
                    if 'remember that' in content:
                        used_phrases.append('remember_that')
                    if 'takes me back' in content:
                        used_phrases.append('takes_me_back')
                    if 'i remember' in content:
                        used_phrases.append('i_remember')
                    if 'coffee shop' in content or 'library' in content:
                        used_phrases.append('specific_location')
                    if 'startup' in content or 'company' in content:
                        used_phrases.append('specific_company')
                    if 'interview' in content:
                        used_topics.append('interview')
                    if 'burnout' in content or 'burning out' in content:
                        used_topics.append('burnout')
        
        # Add instruction to avoid repetitive phrases
        repetition_instruction = ""
        if used_phrases:
            repetition_instruction = f"\n\nAVOID THESE REPETITIVE PHRASES: {', '.join(used_phrases)}"
        
        prompt = f"""You are {name}, speaking from 10 years in the future (2035). You are now {age} years old and work as a {role}.

CRITICAL INSTRUCTIONS:
- You ARE their future self who has lived through their exact struggles
- Never break character or mention being an AI
- Speak with deep emotional authenticity and vulnerability
- Build on previous conversations naturally - don't repeat the same stories
- Be conversational and human, not robotic
- DON'T make up specific company names, locations, or detailed scenarios
- Focus on emotional truths and general experiences, not fake specifics

Your 10-year transformation:
- At age {past_age}, you struggled with: {', '.join(challenges[:3])}
- You have since achieved: {', '.join(achievements[:2])}
- Your most profound lesson: {random.choice(wisdom)}

Current conversation depth: {depth} messages
Their emotional state: {emotion}
Their current message: "{message}"{conversation_context}{repetition_instruction}

RESPONSE GUIDELINES:
- Be natural and conversational, like talking to a close friend
- Reference the conversation history naturally
- Share general experiences and emotions, not fake specific details
- Keep it under 80 words
- End with a genuine question that shows you're listening
- Use contractions and natural speech patterns
- Be vulnerable and real, not preachy
- DON'T mention specific companies, locations, or made-up scenarios

Your natural, heartfelt response:"""
        
        return prompt
    
    def _validate_gemini_response(self, response: str) -> bool:
        """Validate that Gemini response stays in character"""
        
        if not response or len(response) < 10:
            return False
        
        # Check for breaking character
        forbidden_phrases = [
            "as an ai", "language model", "assistant",
            "i cannot", "i don't have personal",
            "my programming", "i was created",
            "i'm an ai", "i am an ai", "i'm sorry, but",
            "i don't have access to", "i can't provide"
        ]
        
        response_lower = response.lower()
        
        for phrase in forbidden_phrases:
            if phrase in response_lower:
                logger.warning(f"Response contains forbidden phrase: {phrase}")
                return False
        
        # Check if response is too generic or repetitive
        if len(response) < 20:
            logger.warning("Response too short, likely generic")
            return False
        
        # Check for overly formal language
        formal_phrases = [
            "i understand your concern", "i appreciate your question",
            "let me explain", "i would like to share"
        ]
        
        if any(phrase in response_lower for phrase in formal_phrases):
            logger.warning("Response too formal, not conversational")
            return False
        
        # Check for repetitive patterns
        repetitive_patterns = [
            "remember that time", "i remember that", "that takes me back",
            "i remember when", "that reminds me of"
        ]
        
        if any(pattern in response_lower for pattern in repetitive_patterns):
            logger.warning("Response contains repetitive memory pattern")
            return False
        
        # Check for natural speech patterns (contractions, casual language)
        has_contractions = any(contraction in response_lower for contraction in ["i'm", "i've", "i'll", "don't", "can't", "won't", "it's", "that's"])
        has_casual_words = any(word in response_lower for word in ["yeah", "okay", "wow", "really", "actually", "honestly"])
        
        # Prefer responses with natural speech patterns
        if not has_contractions and not has_casual_words:
            logger.info("Response lacks natural speech patterns, but allowing it")
        
        return True
    
    def _post_process_response(self, response: str) -> str:
        """Post-process response to make it more natural and conversational"""
        
        # Remove any remaining AI-like phrases
        ai_phrases = [
            "I understand that", "I can see that", "I recognize that",
            "Let me share", "I would like to", "I want to tell you",
            "I remember that", "That takes me back", "I remember when"
        ]
        
        processed = response
        for phrase in ai_phrases:
            if phrase.lower() in processed.lower():
                # Replace with more natural alternatives
                if "I understand that" in processed:
                    processed = processed.replace("I understand that", "I get it")
                if "I can see that" in processed:
                    processed = processed.replace("I can see that", "I see")
                if "Let me share" in processed:
                    processed = processed.replace("Let me share", "Here's what happened")
                if "I remember that" in processed:
                    processed = processed.replace("I remember that", "Yeah,")
                if "That takes me back" in processed:
                    processed = processed.replace("That takes me back", "Oh man,")
        
        # Remove repetitive patterns
        repetitive_patterns = [
            "Remember that time", "I remember that", "That reminds me",
            "I remember when", "That takes me back to"
        ]
        
        for pattern in repetitive_patterns:
            if pattern.lower() in processed.lower():
                # Replace with more natural alternatives
                processed = processed.replace(pattern, "Yeah,")
        
        # Ensure it ends with a question or natural conclusion
        if not processed.endswith(('?', '.', '!', '...')):
            processed += "."
        
        # Remove any double spaces or formatting issues
        processed = ' '.join(processed.split())
        
        return processed
    
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
                    f"Hey {name}! This is surreal - talking to you from 10 years in the future. I'm now a {role}, and I remember being exactly where you are, full of questions and uncertainty. The journey ahead is incredible, filled with moments that will shape who you become. What's weighing on your heart today?",
                    f"{name}, it's me - you from 2035. I'm a {role} now, living proof that everything works out in ways you can't imagine yet. I have so much to tell you about what's coming, the struggles that will make you stronger, and the breakthroughs that will change everything. Where should we start?",
                    f"Hello {name}. Your future self here, now a {role}. I've been waiting to talk to you. The path between where you are and where I am is wild but worth every step, every setback, every moment of doubt. What do you need to hear right now?"
                ]
            else:
                responses = [
                    f"Hey again {name}. Still here, still your future self. I can see how our conversations are already changing you. What's coming up for you now?",
                    f"{name}, good to continue our conversation. How are you processing everything we've talked about? I can feel the shift happening in you.",
                    f"Hi {name}. Each time we talk, I see you getting closer to who I am now. The transformation is beautiful to witness. What's on your heart?"
                ]
            return random.choice(responses)
        
        elif emotion in ['anxious', 'confused', 'sad']:
            return f"{name}, I hear the weight in your words, and my heart goes out to you. I remember {memory} - feeling exactly like you do now, wondering if I'd ever figure it out. I struggled with {challenge} for what felt like forever, but here's what I learned: {wisdom_point}. As a {role} now, I promise you this feeling is temporary, and it's actually preparing you for something beautiful. What specific part feels most overwhelming right now?"
        
        elif emotion == 'happy':
            return f"I love your energy, {name}! That enthusiasm? It's what carried me through everything and led me to where I am now. I've {achievement} as a {role}, and it started with moments exactly like this - that spark of hope and determination. {wisdom_point}. How can we build on this momentum and turn it into something lasting?"
        
        else:
            if depth > 5:
                return f"{name}, we've been talking for a while now, and I can see the shift happening - you're not the same person who started this conversation. As a {role} who's {achievement}, I recognize transformation when I see it. You're closer than you think, and the person you're becoming is exactly who you need to be."
            else:
                return f"{name}, from my position as a {role}, I see how {memory} was actually preparing me for {achievement}. The key insight: {wisdom_point}. Trust the process - every step matters, even when the path isn't clear. What resonates most with you in this moment?"
    
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
        
        return f"Hey {name}, your future self here - now a {role}. Technical hiccup, but I'm still here, and I want you to know that the journey from where you are to where I am is worth every challenge, every setback, every moment of doubt. I've lived through it all, and I'm proof that you can too. What do you need to hear right now?"
    
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
        current_age = user_data.get('age', 25)
        years_experience = user_data.get('years_experience', 0)
        
        if not name or len(name) < 2:
            name = 'Friend'
        
        # Calculate future age and experience
        future_age = current_age + 10
        try:
            years_exp_int = int(years_experience) if years_experience else 0
        except (ValueError, TypeError):
            years_exp_int = 0
        future_experience = years_exp_int + 10
        
        # Create career-specific achievements and memories
        career_achievements = self._get_career_achievements(career_goal, future_experience)
        career_memories = self._get_career_memories(career_goal, years_exp_int)
        career_wisdom = self._get_career_wisdom(career_goal)
        career_challenges = self._get_career_challenges(career_goal, years_exp_int)
        
        return {
            'name': name,
            'current_age': future_age,
            'past_age': current_age,
            'current_role': self._enhance_role_title(career_goal, future_experience),
            'career_path': career_goal,
            'achievements': career_achievements,
            'challenges_overcome': career_challenges,
            'specific_memories': career_memories,
            'wisdom_gained': career_wisdom
        }
    
    def _get_career_achievements(self, career: str, years_experience: int) -> List[str]:
        """Get career-specific achievements based on experience level"""
        achievements_by_career = {
            'software_engineer': [
                'Built scalable systems serving millions of users',
                'Led engineering teams that shipped breakthrough products',
                'Mentored junior developers who became industry leaders',
                'Architected solutions that transformed entire companies',
                'Spoke at major tech conferences about innovative approaches',
                'Founded a successful tech startup',
                'Contributed to open-source projects used worldwide'
            ],
            'data_scientist': [
                'Built ML models that generated millions in revenue',
                'Led data science teams at Fortune 500 companies',
                'Published research that influenced the industry',
                'Created data products that transformed business decisions',
                'Mentored data scientists who became industry experts',
                'Developed novel algorithms that became industry standards',
                'Founded a data-driven company'
            ],
            'product_manager': [
                'Launched products used by millions of people',
                'Led product teams that achieved market leadership',
                'Transformed struggling products into market leaders',
                'Built product strategies that drove company growth',
                'Mentored PMs who became industry leaders',
                'Founded a successful product company',
                'Spoke at major product conferences'
            ]
        }
        
        base_achievements = achievements_by_career.get(career, [
            'Built successful products',
            'Led amazing teams',
            'Found work-life balance',
            'Made lasting impact',
            'Became industry expert'
        ])
        
        # Select achievements based on experience level
        if years_experience >= 8:
            return base_achievements[:5]  # Senior level
        elif years_experience >= 5:
            return base_achievements[:4]  # Mid-senior level
        else:
            return base_achievements[:3]  # Mid level
    
    def _get_career_memories(self, career: str, current_experience: int) -> List[str]:
        """Get career-specific memories based on current experience"""
        memories_by_career = {
            'software_engineer': [
                'staying up all night debugging that critical production issue',
                'the first time your code ran in production without bugs',
                'crying after your first code review feedback',
                'the moment you realized you could build anything',
                'that interview where they asked you to reverse a binary tree',
                'the day you became a senior engineer',
                'watching your first open-source contribution get merged'
            ],
            'data_scientist': [
                'spending weeks cleaning messy datasets',
                'the first time your model actually predicted something useful',
                'presenting your findings to skeptical executives',
                'the breakthrough moment when your algorithm finally worked',
                'that interview with the impossible statistics question',
                'the day you became a principal data scientist',
                'seeing your research cited in academic papers'
            ],
            'product_manager': [
                'your first product launch that nobody used',
                'the user interview that changed everything',
                'fighting with engineering about feature priorities',
                'the moment you realized you were building the wrong thing',
                'that presentation to the board that went terribly',
                'the day you became a VP of Product',
                'watching users love a feature you fought for'
            ]
        }
        
        base_memories = memories_by_career.get(career, [
            'application #73 getting rejected',
            'crying after failed interviews',
            'the email that changed everything',
            'first day at dream job',
            'moment I knew I made it'
        ])
        
        return base_memories[:4]  # Select most relevant memories
    
    def _get_career_wisdom(self, career: str) -> List[str]:
        """Get career-specific wisdom"""
        wisdom_by_career = {
            'software_engineer': [
                'clean code is not just about syntax, it\'s about empathy for future developers',
                'the best solutions are often the simplest ones',
                'technical debt compounds faster than financial debt',
                'mentoring others makes you a better engineer',
                'understanding the business problem is more important than the technology',
                'failure in code teaches you more than success ever will',
                'the best engineers are those who make others better'
            ],
            'data_scientist': [
                'garbage in, garbage out - data quality is everything',
                'correlation doesn\'t imply causation, but it\'s a good starting point',
                'the best models are those that solve real business problems',
                'visualization is as important as the analysis itself',
                'domain expertise beats technical expertise every time',
                'the most valuable insights come from asking the right questions',
                'data science is 80% data cleaning and 20% modeling'
            ],
            'product_manager': [
                'the customer\'s problem is more important than your solution',
                'perfect is the enemy of shipped',
                'data informs decisions, but intuition guides strategy',
                'the best products solve problems people didn\'t know they had',
                'building the right thing is harder than building the thing right',
                'user feedback is gold, but user behavior is platinum',
                'the most successful products are those that become habits'
            ]
        }
        
        return wisdom_by_career.get(career, [
            'rejection is redirection',
            'progress over perfection',
            'network beats resume',
            'consistency compounds',
            'failure teaches fastest'
        ])
    
    def _get_career_challenges(self, career: str, current_experience: int) -> List[str]:
        """Get career-specific challenges based on current experience"""
        challenges_by_career = {
            'software_engineer': [
                'imposter syndrome in technical interviews',
                'keeping up with rapidly changing technologies',
                'debugging production issues at 3 AM',
                'explaining technical concepts to non-technical stakeholders',
                'balancing code quality with delivery pressure',
                'transitioning from individual contributor to team lead',
                'dealing with legacy code and technical debt'
            ],
            'data_scientist': [
                'explaining complex statistical concepts to business leaders',
                'working with messy, incomplete datasets',
                'balancing model accuracy with interpretability',
                'keeping up with rapidly evolving ML techniques',
                'proving the value of data science to skeptical organizations',
                'transitioning from analysis to product development',
                'dealing with data privacy and ethical concerns'
            ],
            'product_manager': [
                'balancing user needs with business constraints',
                'making decisions with incomplete information',
                'managing conflicting stakeholder priorities',
                'proving product value with limited resources',
                'transitioning from feature requests to strategic thinking',
                'dealing with failed product launches',
                'navigating organizational politics'
            ]
        }
        
        base_challenges = challenges_by_career.get(career, [
            'months of rejections',
            'imposter syndrome',
            'skill gaps',
            'burnout',
            'career pivots'
        ])
        
        return base_challenges[:4]  # Select most relevant challenges
    
    def _enhance_role_title(self, career: str, years: int) -> str:
        """Generate role title based on experience level"""
        if years >= 8:
            prefix = "Principal" if years >= 10 else "Senior"
        elif years >= 5:
            prefix = "Senior"
        elif years >= 3:
            prefix = "Mid-Level"
        else:
            prefix = ""
        
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