import os
import json
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(os.path.join(BASE_DIR, '.env'))


class Config:
    """Configuration management"""
    
    # Replicate Key
    REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "").strip()
    
    # Model IDs
    GEMINI_MODEL = "google/gemini-2.5-flash"
    MINIMAX_MODEL = "minimax/image-01"
    FLUX_KONTEXT_MODEL = "black-forest-labs/flux-kontext-pro"
    SEEDANCE_MODEL = "bytedance/seedance-1-prot"
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    STORIES_DIR = os.path.join(DATA_DIR, "stories")
    SCENES_DIR = os.path.join(DATA_DIR, "scenes")
    IMAGES_DIR = os.path.join(DATA_DIR, "images")
    VIDEOS_DIR = os.path.join(DATA_DIR, "videos")
    CONFIG_DIR = os.path.join(BASE_DIR, "config")
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if not exists"""
        os.makedirs(cls.STORIES_DIR, exist_ok=True)
        os.makedirs(cls.SCENES_DIR, exist_ok=True)
        os.makedirs(cls.IMAGES_DIR, exist_ok=True)
        os.makedirs(cls.VIDEOS_DIR, exist_ok=True)
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.REPLICATE_API_TOKEN:
            raise ValueError("REPLICATE_API_TOKEN not found in .env file")