import json
import re
from datetime import datetime


def clean_json_response(response_text: str) -> str:
    """
    Clean JSON response from LLM (remove markdown fences, etc.)
    
    Args:
        response_text: Raw response text from LLM
        
    Returns:
        str: Cleaned JSON string
    """
    cleaned = response_text.strip()
    
    # Remove markdown code fences
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    
    return cleaned.strip()


def validate_story_structure(story_data: dict) -> bool:
    """
    Validate that story data has the required structure
    
    Args:
        story_data: Story data dictionary from Gemini
        
    Returns:
        bool: True if valid, False otherwise
    """
    required_keys = ["characters", "scenes"]
    
    if not all(key in story_data for key in required_keys):
        print("✗ Missing required keys: 'characters' or 'scenes'")
        return False
    
    # Validate characters
    for idx, char in enumerate(story_data.get("characters", [])):
        required_char_keys = ["characterId", "name", "characterPrompt"]
        if not all(key in char for key in required_char_keys):
            print(f"✗ Character {idx+1} missing required keys: {required_char_keys}")
            return False
    
    # Validate scenes
    scenes = story_data.get("scenes", [])
    
    if len(scenes) == 0:
        print("✗ No scenes found in story")
        return False
    
    # Check scene count (3-6 as per prompt)
    if not (3 <= len(scenes) <= 6):
        print(f"⚠ Warning: Scene count {len(scenes)} outside expected range (3-6)")
    
    # Calculate total duration
    total_duration = sum(scene.get("durationSeconds", 0) for scene in scenes)
    if not (25 <= total_duration <= 65):  # Allow some flexibility
        print(f"⚠ Warning: Total duration {total_duration}s outside expected range (30-60s)")
    
    for idx, scene in enumerate(scenes):
        required_scene_keys = [
            "sceneNumber", "sceneDescription", "characterIds", 
            "settingPrompt", "durationSeconds"
        ]
        if not all(key in scene for key in required_scene_keys):
            print(f"✗ Scene {idx+1} missing required keys: {required_scene_keys}")
            return False
    
    return True


def generate_story_id() -> str:
    """
    Generate unique story ID based on timestamp
    
    Returns:
        str: Unique ID in format YYYYMMDD_HHMMSS
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def save_json(data: dict, filepath: str):
    """
    Save data as formatted JSON file
    
    Args:
        data: Dictionary to save
        filepath: Full path to save file
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(filepath: str) -> dict:
    """
    Load JSON data from file
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        dict: Loaded JSON data
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to readable string
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        str: Formatted duration (e.g., "1m 30s")
    """
    if seconds < 60:
        return f"{seconds}s"
    
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    
    if remaining_seconds == 0:
        return f"{minutes}m"
    
    return f"{minutes}m {remaining_seconds}s"


def sanitize_filename(name: str) -> str:
    """
    Sanitize string to be safe for use as filename
    
    Args:
        name: Original string
        
    Returns:
        str: Sanitized filename-safe string
    """
    # Remove invalid filename characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '', name)
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    # Limit length
    sanitized = sanitized[:50]
    return sanitized
