#!/usr/bin/env python3
"""
StoryForge - pipeline orchestrator

Runs every stage in order:
  1. Story     (Gemini 2.5 Flash)        -> data/stories/story_output.json
  2. Images    (MiniMax image-01)        -> data/images/
  3. Scenes    (FLUX Kontext multi-image) -> data/scenes/
  4. Video     (Seedance 1 Pro)          -> data/videos/

Usage:
  python src/main.py --theme "space adventure"
"""

import argparse

from config import Config
from story_generator import generate_story
from generate_images import StoryProcessor
from generate_scenes import ImageLoader
from generate_video import generate_videos


def banner(title: str):
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def get_theme_from_user() -> str:
    """Ask for a story theme interactively."""
    print("\nEnter a theme for your story (e.g., 'space adventure', 'magical forest', 'underwater mystery')")
    print("Or press Enter to let the model choose.\n")
    return input("Theme: ").strip()


def main():
    parser = argparse.ArgumentParser(description="StoryForge: AI video story generator")
    parser.add_argument("--theme", type=str, help="Story theme (skips the interactive prompt)")
    parser.add_argument("--max-scenes", type=int, default=None,
                        help="Only render video for the first N scenes (default: all)")
    args = parser.parse_args()

    banner("STORYFORGE - AI VIDEO STORY GENERATOR")

    try:
        Config.validate()
    except ValueError as e:
        print(f"\n✗ Configuration error: {e}")
        print("Create a .env file in the project root with REPLICATE_API_TOKEN=<your token>")
        return 1
    Config.ensure_directories()

    theme = args.theme if args.theme is not None else get_theme_from_user()
    print(f"\nTheme: {theme or '(model chooses)'}")

    # Step 1: Story
    banner("STEP 1/4: STORY GENERATION (Gemini)")
    try:
        story_data, story_path = generate_story(theme or None)
    except Exception as e:
        print(f"\n✗ Story generation failed: {e}")
        return 1
    print(f"\nStory saved to: {story_path}")
    print("Characters:")
    for char in story_data.get("characters", []):
        print(f"  - {char.get('name')} ({char.get('characterId')})")
    print(f"Scenes: {len(story_data.get('scenes', []))}")

    # Step 2: Character and background images
    banner("STEP 2/4: CHARACTER & SETTING IMAGES (MiniMax)")
    processor = StoryProcessor()
    processor.story = story_data
    processor.process_characters()
    processor.process_scenes()

    # Step 3: Composite characters into scenes
    banner("STEP 3/4: SCENE COMPOSITING (FLUX Kontext)")
    ImageLoader(story_data).load_images()

    # Step 4: Animate scenes
    banner("STEP 4/4: VIDEO GENERATION (Seedance)")
    clips = generate_videos(story_data, max_scenes=args.max_scenes)

    banner("✓ PIPELINE COMPLETE")
    print(f"Story:  {story_path}")
    print(f"Images: {Config.IMAGES_DIR}")
    print(f"Scenes: {Config.SCENES_DIR}")
    print(f"Clips:  {len(clips)} saved to {Config.VIDEOS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
