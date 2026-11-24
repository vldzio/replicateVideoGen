import argparse
import base64
import json
import os

import requests
from replicate.client import Client

from config import Config


def load_story(filename="story_output.json"):
    """Load the story JSON produced by story_generator.py."""
    story_path = os.path.join(Config.STORIES_DIR, filename)
    try:
        with open(story_path, "r", encoding="utf-8") as f:
            story = json.load(f)
        print(f"✓ Loaded story from {story_path}")
        return story
    except FileNotFoundError:
        print(f"✗ Story file not found at {story_path}")
        return {}


def to_data_uri(filepath):
    """Encode a local image as a data URI for Replicate."""
    with open(filepath, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return f"data:application/octet-stream;base64,{data}"


def videoGen(prompt: str, model_id: str, save_path: str, url_save_path: str,
             duration: int = 5, image_path: str = None):
    """Generate a video clip, save the video to disk and save its URL."""
    input_data = {
        "fps": 24,
        "prompt": prompt,
        "duration": duration,  # 5 or 10 seconds
        "resolution": "480p",
        "aspect_ratio": "16:9",
        "camera_fixed": False
    }
    if image_path and os.path.exists(image_path):
        # Animate from the composited scene image (image-to-video)
        input_data["image"] = to_data_uri(image_path)

    print(f"Generating {duration}s video for prompt:\n{prompt[:60]}...")

    try:
        client = Client(api_token=Config.REPLICATE_API_TOKEN)
        output = client.run(model_id, input=input_data)
        video_url = output if isinstance(output, str) else (output[0] if output else None)
        if video_url is not None and not isinstance(video_url, str):
            video_url = str(video_url)

        if not video_url:
            print(" No video URL returned from model")
            return None

        print(f"Video URL: {video_url}")

        with open(url_save_path, "w", encoding="utf-8") as f:
            f.write(video_url)
        print(f"Video URL saved: {url_save_path}")

        response = requests.get(video_url, timeout=120)
        response.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(response.content)
        print(f"Video saved: {save_path}")
        return save_path

    except Exception as e:
        print(f"Failed to generate video: {e}")
        return None


def generate_videos(story=None, max_scenes=None):
    """Generate one clip per scene. Returns the list of saved video paths."""
    Config.ensure_directories()
    if story is None:
        story = load_story()

    scenes = story.get("scenes", [])
    if max_scenes is not None:
        scenes = scenes[:max_scenes]

    saved = []
    for idx, scene in enumerate(scenes, start=1):
        scene_number = scene.get("sceneNumber", idx)
        scene_description = scene.get("sceneDescription", "")
        starting_setting = scene.get("startingSettingPrompt", "")
        ending_setting = scene.get("endingSettingPrompt", "")
        motion_prompt = scene.get("motionPrompt", "")
        # Seedance accepts clips of 5 or 10 seconds
        scene_duration = 10 if scene.get("durationSeconds", 5) > 7 else 5

        full_prompt = f"{scene_description} {starting_setting} {ending_setting} {motion_prompt}"

        video_path = os.path.join(Config.VIDEOS_DIR, f"scene_{scene_number}.mp4")
        url_path = os.path.join(Config.VIDEOS_DIR, f"scene_{scene_number}_url.txt")
        scene_image = os.path.join(Config.SCENES_DIR, f"scene_{scene_number}_scene.png")

        print(f"\nScene {scene_number} ({idx}/{len(scenes)})")
        result = videoGen(full_prompt, Config.SEEDANCE_MODEL, video_path, url_path,
                          scene_duration, scene_image)
        if result:
            saved.append(result)

    print(f"\n✓ Generated {len(saved)}/{len(scenes)} scene clips in {Config.VIDEOS_DIR}")
    return saved


def main():
    parser = argparse.ArgumentParser(description="Generate Seedance clips for every scene")
    parser.add_argument("--max-scenes", type=int, default=None,
                        help="Only generate the first N scenes (default: all)")
    args = parser.parse_args()
    generate_videos(max_scenes=args.max_scenes)


if __name__ == "__main__":
    main()
