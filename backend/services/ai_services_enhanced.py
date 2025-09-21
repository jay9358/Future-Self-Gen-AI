# Enhanced AI Services - Hugging Face and Google Only
import os
import logging
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
import time
import random

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent.parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    pass
except Exception as e:
    print(f"Could not load .env file: {e}")

logger = logging.getLogger(__name__)

class EnhancedAIService:
    """Enhanced AI service using only Hugging Face and Google models"""
    
    def __init__(self):
        self.hf_pipeline = None
        self.hf_model_loaded = False
        self.google_model = None
        self.google_model_loaded = False
        self.initialize_models()
    
    def initialize_models(self):
        """Initialize both Hugging Face and Google models"""
        self._initialize_huggingface()
        self._initialize_google()
    
    def _initialize_huggingface(self):
        """Initialize Hugging Face models"""
        try:
            from transformers import pipeline
            import torch
            
            logger.info("Loading Hugging Face model...")
            
            # Try multiple models in order of preference
            models_to_try = [
                "distilgpt2",                 # Most compatible
                "gpt2",                       # Reliable fallback
                "microsoft/DialoGPT-small",   # Lighter alternative
            ]
            
            for model_name in models_to_try:
                try:
                    logger.info(f"Attempting to load HF model: {model_name}")
                    
                    self.hf_pipeline = pipeline(
                        "text-generation",
                        model=model_name,
                        device=-1,  # CPU
                        max_length=200,
                        do_sample=True,
                        temperature=0.8,
                        top_p=0.9,
                        repetition_penalty=1.1
                    )
                    
                    self.hf_model_loaded = True
                    logger.info(f"✅ Successfully loaded Hugging Face model: {model_name}")
                    return True
                    
                except Exception as e:
                    logger.warning(f"Failed to load HF model {model_name}: {e}")
                    continue
            
            logger.warning("❌ Failed to load any Hugging Face model")
            self.hf_model_loaded = False
            return False
            
        except ImportError:
            logger.warning("⚠️  Transformers library not available")
            self.hf_model_loaded = False
            return False
        except Exception as e:
            logger.error(f"❌ Error initializing Hugging Face models: {e}")
            self.hf_model_loaded = False
            return False
    
    def _initialize_google(self):
        """Initialize Google Gemini models"""
        try:
            import google.generativeai as genai
            
            # Get API key from environment
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                logger.warning("⚠️  Google API key not found in environment variables")
                self.google_model_loaded = False
                return False
            
            # Configure Google AI
            genai.configure(api_key=api_key)
            
            # Try different models
            models_to_try = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
            
            for model_name in models_to_try:
                try:
                    logger.info(f"Attempting to load Google model: {model_name}")
                    self.google_model = genai.GenerativeModel(model_name)
                    
                    # Test the model
                    test_response = self.google_model.generate_content("Hello")
                    if test_response and test_response.text:
                        self.google_model_loaded = True
                        logger.info(f"✅ Successfully loaded Google model: {model_name}")
                        return True
                        
                except Exception as e:
                    logger.warning(f"Failed to load Google model {model_name}: {e}")
                    continue
            
            logger.warning("❌ Failed to load any Google model")
            self.google_model_loaded = False
            return False
            
        except ImportError:
            logger.warning("⚠️  Google Generative AI library not available")
            self.google_model_loaded = False
            return False
        except Exception as e:
            logger.error(f"❌ Error initializing Google models: {e}")
            self.google_model_loaded = False
            return False
    
    def is_model_available(self) -> bool:
        """Check if any AI model is available"""
        return self.hf_model_loaded or self.google_model_loaded
    
    def generate_future_self_response(self, message: str, persona: Dict[str, Any], 
                                    conversation_history: List[Dict] = None) -> Optional[str]:
        """Generate response as user's future self using available models"""
        
        if not self.is_model_available():
            logger.warning("No AI models available")
            return None
        
        # Build comprehensive prompt for future self persona
        prompt = self._build_future_self_prompt(message, persona, conversation_history)
        
        # Try Google first (usually better quality), then Hugging Face
        if self.google_model_loaded:
            try:
                response = self._generate_with_google(prompt)
                if response and self._validate_response(response, persona):
                    logger.info("✅ Generated response using Google model")
                    return response
            except Exception as e:
                logger.warning(f"Google model failed: {e}")
        
        if self.hf_model_loaded:
            try:
                response = self._generate_with_huggingface(prompt)
                if response and self._validate_response(response, persona):
                    logger.info("✅ Generated response using Hugging Face model")
                    return response
            except Exception as e:
                logger.warning(f"Hugging Face model failed: {e}")
        
        logger.error("All AI models failed to generate response")
        return None
    
    def _build_future_self_prompt(self, message: str, persona: Dict[str, Any], 
                                 conversation_history: List[Dict] = None) -> str:
        """Build comprehensive prompt for future self persona"""
        
        name = persona.get('name', 'Friend')
        role = persona.get('current_role', 'Professional')
        achievements = persona.get('achievements', [])
        wisdom = persona.get('wisdom_gained', [])
        memories = persona.get('specific_memories', [])
        
        # Build context
        context_parts = [
            f"You are {name}, now {persona.get('current_age', 35)} years old.",
            f"You are a successful {role} who started as a {persona.get('previous_role', 'student')}.",
            f"You are speaking to your past self from 10 years ago.",
            f"You have achieved: {', '.join(achievements[:3]) if achievements else 'great things'}.",
            f"Your wisdom includes: {', '.join(wisdom[:2]) if wisdom else 'valuable lessons'}.",
            f"You remember: {', '.join(memories[:2]) if memories else 'your journey'}."
        ]
        
        # Add conversation history
        if conversation_history and len(conversation_history) > 0:
            recent_history = conversation_history[-2:]  # Last 2 exchanges
            history_text = ""
            for exchange in recent_history:
                role_name = exchange.get('role', 'user')
                content = exchange.get('content', '')
                if role_name == 'user':
                    history_text += f"Past {name}: {content}\n"
                else:
                    history_text += f"Future {name}: {content}\n"
            context_parts.append(f"Recent conversation:\n{history_text}")
        
        context = " ".join(context_parts)
        
        # Create the full prompt
        prompt = f"""{context}

Past {name} asks: "{message}"

Future {name} responds with warmth, wisdom, and personal connection:"""
        
        return prompt
    
    def _generate_with_google(self, prompt: str) -> Optional[str]:
        """Generate response using Google Gemini"""
        try:
            response = self.google_model.generate_content(
                prompt,
                generation_config={
                    'max_output_tokens': 300,
                    'temperature': 0.8,
                    'top_p': 0.9,
                }
            )
            
            if response and response.text:
                return response.text.strip()
            return None
            
        except Exception as e:
            logger.error(f"Google generation error: {e}")
            return None
    
    def _generate_with_huggingface(self, prompt: str) -> Optional[str]:
        """Generate response using Hugging Face"""
        try:
            result = self.hf_pipeline(
                prompt, 
                max_length=len(prompt.split()) + 100, 
                num_return_sequences=1,
                do_sample=True,
                temperature=0.8,
                top_p=0.9,
                repetition_penalty=1.1
            )
            
            generated_text = result[0]['generated_text']
            
            # Extract only the response part
            if "responds with warmth, wisdom, and personal connection:" in generated_text:
                response = generated_text.split("responds with warmth, wisdom, and personal connection:")[-1].strip()
            else:
                response = generated_text.replace(prompt, '').strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Hugging Face generation error: {e}")
            return None
    
    def _validate_response(self, response: str, persona: Dict[str, Any]) -> bool:
        """Validate that response is appropriate for future self persona"""
        if not response or len(response) < 20:
            return False
        
        # Check for future self indicators
        future_indicators = ['future', '10 years', 'now', 'became', 'achieved', 'learned']
        if not any(indicator in response.lower() for indicator in future_indicators):
            return False
        
        # Check for personal connection
        personal_indicators = ['you', 'your', 'i', 'me', 'we', 'our']
        if not any(indicator in response.lower() for indicator in personal_indicators):
            return False
        
        # Check for reasonable length
        if len(response) > 500:
            return False
        
        return True
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get status of all models"""
        return {
            'huggingface_available': self.hf_model_loaded,
            'google_available': self.google_model_loaded,
            'any_model_available': self.is_model_available()
        }

# Create global instance
enhanced_ai_service = EnhancedAIService()
