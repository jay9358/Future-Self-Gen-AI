# Configuration settings
import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env file from project root (two levels up from config/)
    env_path = Path(__file__).resolve().parent.parent.parent / '.env'
    load_dotenv(env_path)
    print(f"✅ Config: Environment variables loaded from: {env_path}")
except ImportError:
    print("⚠️  Config: python-dotenv not installed. Install with: pip install python-dotenv")
except Exception as e:
    print(f"⚠️  Config: Could not load .env file: {e}")

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Upload folders
UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads'
AVATAR_FOLDER = BASE_DIR / 'static' / 'avatars'
RESUME_FOLDER = BASE_DIR / 'static' / 'resumes'

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
RESUME_EXTENSIONS = {'pdf', 'docx', 'txt'}

# API Keys
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')
