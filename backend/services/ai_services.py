# AI Services - Optimized for Speed and Performance
import os
import asyncio
import logging
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List
from functools import lru_cache
import time

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env file from project root (three levels up from services/)
    env_path = Path(__file__).resolve().parent.parent.parent / '.env'
    load_dotenv(env_path)
    print(f"✅ AI Services: Environment variables loaded from: {env_path}")
except ImportError:
    print("⚠️  AI Services: python-dotenv not installed. Install with: pip install python-dotenv")
except Exception as e:
    print(f"⚠️  AI Services: Could not load .env file: {e}")

logger = logging.getLogger(__name__)

# Response cache for faster repeated queries
_response_cache = {}
_cache_ttl = 3600  # 1 hour cache TTL

# Rate limiting for free tier (5 requests per minute)
import time
from collections import deque
from threading import Lock

_rate_limit_queue = deque()
_rate_limit_lock = Lock()
MAX_REQUESTS_PER_MINUTE = 4  # Leave 1 request buffer for safety

# Configure APIs with optimized settings
claude_client = None
gemini_model = None
gemini_models = {}  # Multiple model instances for load balancing

try:
    import anthropic
    # Check if API key exists
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key:
        try:
            # Initialize Claude client with only the API key
            # The current version of anthropic (0.18.1) only supports api_key parameter
            claude_client = anthropic.Anthropic(api_key=api_key)
            logger.info("✅ Claude API initialized successfully")
            logger.info(f"Claude API Key: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '***'}")
            logger.info(f"Anthropic version: {anthropic.__version__}")
        except Exception as init_error:
            logger.error(f"❌ Claude initialization failed: {init_error}")
            logger.error(f"Init error type: {type(init_error).__name__}")
            logger.error(f"Init error args: {init_error.args}")
            
            # Try alternative initialization method without any extra parameters
            try:
                # Create client with just the API key - no other parameters
                claude_client = anthropic.Anthropic(api_key=api_key)
                logger.info("✅ Claude API initialized with alternative method")
            except Exception as alt_error:
                logger.error(f"❌ Alternative Claude initialization also failed: {alt_error}")
                logger.error(f"Alt error type: {type(alt_error).__name__}")
                logger.error(f"Alt error args: {alt_error.args}")
                claude_client = None
    else:
        logger.warning("❌ ANTHROPIC_API_KEY not found in environment variables")
        logger.info("Available environment variables:")
        for key in os.environ:
            if 'ANTHROPIC' in key or 'CLAUDE' in key:
                logger.info(f"  {key}: {os.environ[key][:8]}...")
except ImportError:
    logger.warning("❌ Anthropic library not installed. Install with: pip install anthropic")
except Exception as e:
    logger.warning(f"❌ Claude API not configured: {e}")
    logger.error(f"Full error details: {e}")
    logger.error(f"Error type: {type(e).__name__}")

try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    
    # Initialize multiple Gemini models for load balancing
    gemini_models = {
        'flash': genai.GenerativeModel('gemini-1.5-flash'),
        'pro': genai.GenerativeModel('gemini-1.5-pro'),
        'flash-8b': genai.GenerativeModel('gemini-1.5-flash-8b')
    }
    gemini_model = gemini_models['flash']  # Default to fastest model
    logger.info("Gemini API initialized successfully with multiple models")
except ImportError:
    logger.warning("Google Generative AI library not installed")
except Exception as e:
    logger.warning(f"Gemini API not configured: {e}")

def get_claude_client():
    """Get Claude client instance"""
    return claude_client

def get_gemini_model(model_name='flash'):
    """Get Gemini model instance with load balancing"""
    return gemini_models.get(model_name, gemini_model)

def get_all_gemini_models():
    """Get all available Gemini models"""
    return gemini_models

def is_ai_available():
    """Check if any AI service is available"""
    return claude_client is not None or gemini_model is not None

def _generate_cache_key(prompt: str, model: str, career: str) -> str:
    """Generate cache key for response caching"""
    content = f"{prompt}_{model}_{career}"
    return hashlib.md5(content.encode()).hexdigest()

def _get_cached_response(cache_key: str) -> Optional[str]:
    """Get cached response if available and not expired"""
    if cache_key in _response_cache:
        cached_data = _response_cache[cache_key]
        if time.time() - cached_data['timestamp'] < _cache_ttl:
            return cached_data['response']
        else:
            del _response_cache[cache_key]
    return None

def _cache_response(cache_key: str, response: str):
    """Cache response with timestamp"""
    _response_cache[cache_key] = {
        'response': response,
        'timestamp': time.time()
    }

async def generate_response_async(prompt: str, career: str, model_preference: str = 'auto') -> str:
    """Generate AI response asynchronously with caching and load balancing"""
    # Generate cache key
    cache_key = _generate_cache_key(prompt, model_preference, career)
    
    # Check cache first
    cached_response = _get_cached_response(cache_key)
    if cached_response:
        logger.info("Returning cached response")
        return cached_response
    
    # Try multiple models in parallel for fastest response
    tasks = []
    
    if claude_client and model_preference in ['auto', 'claude']:
        tasks.append(_try_claude_async(prompt, career))
    
    if gemini_models and model_preference in ['auto', 'gemini']:
        # Try fastest model first
        tasks.append(_try_gemini_async(prompt, career, 'flash'))
        if len(tasks) < 2:  # Only add more if we don't have many tasks
            tasks.append(_try_gemini_async(prompt, career, 'flash-8b'))
    
    if not tasks:
        return _get_fallback_response(career, prompt)
    
    # Wait for first successful response
    try:
        # Use asyncio.wait_for with a shorter timeout
        result = await asyncio.wait_for(
            asyncio.gather(*tasks, return_exceptions=True),
            timeout=8.0  # 8 second timeout
        )
        
        # Find first successful response
        for response in result:
            if isinstance(response, str) and response.strip():
                _cache_response(cache_key, response)
                return response
                
    except asyncio.TimeoutError:
        logger.warning("All AI models timed out")
    except Exception as e:
        logger.error(f"Error in async response generation: {e}")
    
    # Fallback response
    fallback = _get_fallback_response(career, prompt)
    _cache_response(cache_key, fallback)
    return fallback

async def _try_claude_async(prompt: str, career: str) -> Optional[str]:
    """Try Claude API asynchronously with rate limiting"""
    try:
        if not claude_client:
            return None
        
        # Check rate limit before making request
        if not _can_make_request():
            logger.info("Rate limit reached, skipping Claude API call")
            return None
            
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: _make_claude_request(prompt)
        )
        
        if response:
            _record_request()  # Record successful request
            return response
        return None
        
    except Exception as e:
        logger.error(f"Claude async error: {e}")
        return None

def _make_claude_request(prompt: str) -> Optional[str]:
    """Make a Claude API request with optimized settings for free tier"""
    try:
        # Use Claude Haiku 3.5 for free tier (most efficient)
        response = claude_client.messages.create(
            model="claude-3-5-haiku-20241022",  # Most efficient model for free tier
            max_tokens=300,  # Reduced for faster response and lower cost
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        logger.error(f"Claude request error: {e}")
        return None

async def _try_gemini_async(prompt: str, career: str, model_name: str = 'flash') -> Optional[str]:
    """Try Gemini API asynchronously with optimized settings"""
    try:
        model = get_gemini_model(model_name)
        if not model:
            return None
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=300,  # Reduced for faster response
                    temperature=0.7,
                    top_p=0.8,
                    top_k=40
                )
            )
        )
        
        if response and hasattr(response, 'text') and response.text:
            return response.text
        return None
    except Exception as e:
        logger.error(f"Gemini async error ({model_name}): {e}")
        return None

def _get_fallback_response(career: str, prompt: str) -> str:
    """Get optimized fallback response"""
    career_titles = {
        'software_engineer': 'Software Engineer',
        'data_scientist': 'Data Scientist', 
        'doctor': 'Medical Doctor',
        'entrepreneur': 'Entrepreneur',
        'teacher': 'Teacher'
    }
    
    title = career_titles.get(career, career.replace('_', ' ').title())
    
    fallback_responses = [
        f"Hello! I'm you from 10 years in the future as a successful {title}. The journey has been incredible - challenging but so rewarding. I've grown both personally and professionally. What would you like to know about our future?",
        f"Hey there! It's me, your future self, now a {title}. I remember being where you are now. The path wasn't always clear, but every step led to amazing opportunities. Ask me anything!",
        f"Hi! I'm you 10 years from now, working as a {title}. The transformation has been remarkable. I've learned so much and achieved things I never thought possible. What's on your mind?"
    ]
    
    # Use prompt hash to consistently return same response for same question
    prompt_hash = hash(prompt) % len(fallback_responses)
    return fallback_responses[prompt_hash]

@lru_cache(maxsize=100)
def get_optimized_prompt(career: str, question: str, context: Dict[str, Any]) -> str:
    """Generate optimized prompt with caching"""
    from models.career_database import CAREER_DATABASE
    career_info = CAREER_DATABASE.get(career, {})
    
    # Shorter, more focused prompt for faster processing
    return f"""You are {career_info.get('title', career)} 10 years in the future. Be encouraging and specific.

Career: {career}
Question: {question}

Respond in first person, under 150 words. Include specific advice and encouragement."""

def clear_cache():
    """Clear response cache"""
    global _response_cache
    _response_cache.clear()
    logger.info("Response cache cleared")

def get_claude_client():
    """Get Claude client instance"""
    return claude_client

def get_gemini_model(model_name: str = 'flash'):
    """Get Gemini model instance"""
    return gemini_models.get(model_name, gemini_model)

def is_ai_available() -> bool:
    """Check if any AI service is available"""
    return claude_client is not None or gemini_model is not None

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    return {
        'cache_size': len(_response_cache),
        'cache_ttl': _cache_ttl,
        'available_models': list(gemini_models.keys()) + (['claude'] if claude_client else []),
        'rate_limit_queue_size': len(_rate_limit_queue)
    }

def _can_make_request() -> bool:
    """Check if we can make a request within rate limits"""
    with _rate_limit_lock:
        current_time = time.time()
        
        # Remove requests older than 1 minute
        while _rate_limit_queue and current_time - _rate_limit_queue[0] > 60:
            _rate_limit_queue.popleft()
        
        # Check if we're under the limit
        return len(_rate_limit_queue) < MAX_REQUESTS_PER_MINUTE

def _record_request():
    """Record a request for rate limiting"""
    with _rate_limit_lock:
        _rate_limit_queue.append(time.time())

def _wait_for_rate_limit():
    """Wait if we're at the rate limit"""
    if not _can_make_request():
        # Calculate wait time
        with _rate_limit_lock:
            if _rate_limit_queue:
                oldest_request = _rate_limit_queue[0]
                wait_time = 60 - (time.time() - oldest_request) + 1  # Add 1 second buffer
                if wait_time > 0 and wait_time < 30:  # Only wait if it's reasonable
                    logger.info(f"Rate limit reached, waiting {wait_time:.1f} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.info("Rate limit wait time too long, skipping wait")
