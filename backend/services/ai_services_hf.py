# AI Services - Hugging Face Only
import os
import logging
import json
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
_cache_ttl = 300  # 5 minute cache TTL

# Hugging Face models
hf_pipeline = None
hf_model_loaded = False

def initialize_huggingface_models():
    """Initialize Hugging Face models for AI responses"""
    global hf_pipeline, hf_model_loaded
    
    try:
        from transformers import pipeline
        import torch
        
        logger.info("Loading Hugging Face models for AI responses...")
        
        # Try to load a text generation model
        try:
            hf_pipeline = pipeline(
                "text-generation",
                model="distilgpt2",
                device=-1,  # CPU
                max_length=200,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.1
            )
            
            hf_model_loaded = True
            logger.info("✅ Hugging Face models loaded successfully")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to load Hugging Face model: {e}")
            hf_model_loaded = False
            return False
            
    except ImportError:
        logger.warning("Transformers library not available")
        hf_model_loaded = False
        return False
    except Exception as e:
        logger.error(f"Error initializing Hugging Face models: {e}")
        hf_model_loaded = False
        return False

def get_huggingface_pipeline():
    """Get the Hugging Face pipeline"""
    global hf_pipeline, hf_model_loaded
    
    if not hf_model_loaded:
        initialize_huggingface_models()
    
    return hf_pipeline if hf_model_loaded else None

def generate_ai_response(message: str, context: str = "", max_tokens: int = 150) -> Optional[str]:
    """Generate AI response using Hugging Face models"""
    try:
        pipeline = get_huggingface_pipeline()
        if not pipeline:
            logger.warning("Hugging Face pipeline not available")
            return None
        
        # Create prompt
        prompt = f"User: {message}\n"
        if context:
            prompt += f"Context: {context}\n"
        prompt += "Assistant:"
        
        # Generate response
        result = pipeline(prompt, max_length=len(prompt.split()) + max_tokens, num_return_sequences=1)
        generated_text = result[0]['generated_text']
        
        # Extract only the assistant's response
        if "Assistant:" in generated_text:
            response = generated_text.split("Assistant:")[-1].strip()
        else:
            response = generated_text.replace(prompt, '').strip()
        
        # Clean up the response
        response = _clean_response(response)
        
        return response if response and len(response) > 10 else None
        
    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        return None

def _clean_response(response: str) -> str:
    """Clean up the generated response"""
    if not response:
        return ""
    
    # Remove common artifacts
    response = response.replace("User:", "").replace("Assistant:", "").strip()
    
    # Remove incomplete sentences at the end
    if response and not response.endswith(('.', '!', '?')):
        # Find the last complete sentence
        last_sentence_end = max(response.rfind('.'), response.rfind('!'), response.rfind('?'))
        if last_sentence_end > 0:
            response = response[:last_sentence_end + 1]
    
    return response.strip()

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    return {
        "cache_size": len(_response_cache),
        "cache_ttl": _cache_ttl,
        "hf_model_loaded": hf_model_loaded
    }

def clear_cache():
    """Clear the response cache"""
    global _response_cache
    _response_cache.clear()
    logger.info("Response cache cleared")

# Initialize models on import
initialize_huggingface_models()
