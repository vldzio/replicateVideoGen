#!/usr/bin/env python3
"""
Video Story Generator - Main Orchestrator
"""

import argparse
from src.story_generator import StoryGenerator


def get_theme_from_user() -> str:
    """Get story theme from user input"""
    print("="*60)
    print("AI VIDEO STORY GENERATOR")
    print("="*60)
    print("\nEnter a theme for your story (e.g., 'space adventure', 'magical forest', 'underwater mystery')")
    print("Or press Enter for a random theme.\n")
    
    theme = input("Theme: ").strip()
    
    if not theme:
        theme = "random"
        print(f"Using default theme: {theme}")
    
    return theme


def main():
    """Main entry point"""
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="AI Video Story Generator")
    parser.add_argument("--theme", type=str, help="Story theme (skip interactive prompt)")
    args = parser.parse_args()
    
    # Get theme
    if args.theme:
        theme = args.theme
        print("="*60)
        print("AI VIDEO STORY GENERATOR")
        print("="*60)
        print(f"\nTheme: {theme}\n")
    else:
        theme = get_theme_from_user()
    
    print()
    
    # Step 1: Generate Story
    print("STEP 1: STORY GENERATION")
    print("-"*60)
    
    try:
        # StoryGenerator now handles validation and setup internally
        story_gen = StoryGenerator()
        story_data, story_path = story_gen.generate_and_save(theme)
        
        print()
        print("="*60)
        print("✓ STORY GENERATION COMPLETE")
        print("="*60)
        print(f"Story saved to: {story_path}")
        print(f"\nCharacters:")
        for char in story_data['characters']:
            print(f"  - {char['name']} ({char['characterId']})")
        print(f"\nScenes: {len(story_data['scenes'])}")
        
    except ValueError as e:
        print(f"\n✗ Configuration error: {e}")
        print("\nMake sure you have set REPLICATE_API_TOKEN in your .env file")
        return
    except Exception as e:
        print(f"\n✗ Story generation failed: {e}")
        return
    
    # TODO: Step 2 - Image Generation (Minimax)
    # TODO: Step 3 - Image Compositing (FLUX Kontext)
    # TODO: Step 4 - Video Generation (Seedance)
    
    print("\n✓ Pipeline complete!")


if __name__ == "__main__":
    main()
