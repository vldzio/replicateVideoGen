import os
import json
import replicate
import requests
from config import Config

Config.ensure_directories()

# Load story
story_path = os.path.join(Config.STORIES_DIR, "story_output.json")
try:
    with open(story_path, "r", encoding="utf-8") as f:
        story = json.load(f)
        print(f"✓ Loaded story from {story_path}")
except FileNotFoundError:
    print(f"✗ Story file not found at {story_path}")
    story = {}


def videoGen(prompt: str, model_id: str, save_path: str, url_save_path: str, duration: int = 5, input_image_path: str = None):
    Config.validate()
    input_data = {
        "fps": 24,
        "prompt": prompt,
        "duration": duration,
        "resolution": "480p",
        "aspect_ratio": "16:9",
        "camera_fixed": False
    }

    if input_image_path and os.path.exists(input_image_path):
        # Pass visual reference if available
        with open(input_image_path, "rb") as img_file:
            input_data["image"] = img_file

    print(f"Generating {duration}s video clip for:\n{prompt[:60]}...")

    try:
        output = replicate.run(model_id, input=input_data)
        video_url = output if isinstance(output, str) else (output[0] if output else None)

        if not video_url:
            print("No video URL returned from model")
            return

        print(f"Video URL: {video_url}")

        with open(url_save_path, "w", encoding="utf-8") as f:
            f.write(video_url)

        response = requests.get(video_url, timeout=180)
        response.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(response.content)
        print(f"✓ Video saved: {save_path}")

    except Exception as e:
        print(f"Failed to generate video: {e}")


def main():
    scenes = story.get("scenes", [])
    for idx, scene in enumerate(scenes, start=1):
        scene_number = scene.get("sceneNumber", idx)
        scene_description = scene.get("sceneDescription", "")
        startingSetting = scene.get("startingSettingPrompt", "")
        endingSetting = scene.get("endingSettingPrompt", "")
        motionPrompt = scene.get("motionPrompt", "")
        scene_duration = min(scene.get("durationSeconds", 5), 10)

        full_prompt = f"{scene_description} {startingSetting} {endingSetting} {motionPrompt}".strip()

        video_filename = f"scene_{scene_number}.mp4"
        video_path = os.path.join(Config.VIDEOS_DIR, video_filename)

        url_filename = f"scene_{scene_number}_url.txt"
        url_path = os.path.join(Config.VIDEOS_DIR, url_filename)

        # Check if stitched composite exists
        composite_path = os.path.join(Config.SCENES_DIR, f"scene_{scene_number}_scene.png")
        input_image = composite_path if os.path.exists(composite_path) else None

        videoGen(full_prompt, Config.SEEDANCE_MODEL, video_path, url_path, scene_duration, input_image)


if __name__ == "__main__":
    main()
