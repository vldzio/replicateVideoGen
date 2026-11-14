#!/usr/bin/env python3
"""
Video Story Generator - Full Orchestrator Pipeline
Connects Gemini (Story), MiniMax (Art), FLUX Kontext (Compositing), and Seedance (Video).
"""

import argparse
import os
from src.config import Config
from src.story_generator import StoryGenerator
from src.generate_images import StoryProcessor
from src.generate_scenes import ImageLoader
from src.generate_video import main as run_video_gen


def get_theme_from_user() -> str:
    print("=" * 60)
    print("AI VIDEO STORY GENERATOR - STORYFORGE")
    print("=" * 60)
    print("\nEnter a theme for your story (e.g., 'space adventure', 'magical forest', 'cyberpunk discovery')")
    print("Or press Enter for default.\n")
    
    theme = input("Theme: ").strip()
    if not theme:
        theme = "An artistic young woman uncovers hope in an abandoned urban community garden"
        print(f"Using default theme: {theme}")
    return theme


def main():
    parser = argparse.ArgumentParser(description="StoryForge End-to-End Orchestrator")
    parser.add_argument("--theme", type=str, help="Story theme")
    parser.add_argument("--skip-video", action="store_true", help="Skip heavy video generation")
    args = parser.parse_args()
    
    theme = args.theme or get_theme_from_user()
    
    # Validate API Token
    try:
        Config.validate()
    except ValueError as e:
        print(f"\n✗ Configuration error: {e}")
        print("Please set REPLICATE_API_TOKEN in your .env file.")
        return

    # STEP 1: Story Generation
    print("\n" + "=" * 60)
    print("STEP 1: STORY GENERATION (Gemini 2.5 via Replicate)")
    print("=" * 60)
    story_gen = StoryGenerator()
    story_data, story_path = story_gen.generate_and_save(theme)
    print(f"✓ Story generated with {len(story_data.get('characters', []))} characters and {len(story_data.get('scenes', []))} scenes.")

    # STEP 2: Character & Setting Art
    print("\n" + "=" * 60)
    print("STEP 2: CHARACTER & SETTING ART (MiniMax via Replicate)")
    print("=" * 60)
    art_processor = StoryProcessor()
    art_processor.load_story()
    art_processor.process_characters()
    art_processor.process_scenes()
    print("✓ Character and scene background art generation complete.")

    # STEP 3: Scene Compositing (FLUX Kontext)
    print("\n" + "=" * 60)
    print("STEP 3: SCENE COMPOSITING (FLUX Kontext via Replicate)")
    print("=" * 60)
    image_loader = ImageLoader(story_data)
    image_loader.load_images()
    print("✓ Scene stitching and compositing complete.")

    # STEP 4: Video Clip Rendering
    if not args.skip_video:
        print("\n" + "=" * 60)
        print("STEP 4: VIDEO RENDERING (Seedance via Replicate)")
        print("=" * 60)
        run_video_gen()
        print("✓ Video clips rendered successfully.")
    else:
        print("\n[Skipping video rendering flag set]")

    print("\n" + "=" * 60)
    print("✓ STORYFORGE PIPELINE COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
