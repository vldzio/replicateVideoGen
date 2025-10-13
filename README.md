# AI-Powered Short-Form Video Story Generator

An automated Python pipeline that transforms user themes into complete 30-60 second videos for social media. Uses AI models from Replicate to generate characters, scenes, and animated video clips.

## Overview

Input a simple theme (e.g., "magical forest adventure") and the system automatically:
- Generates a structured story with characters and scenes
- Creates character images and scene backgrounds
- Composites characters into scenes
- Produces animated video clips with motion
- Stitches everything into a final video

## Tech Stack

- **Python** - Core language
- **Replicate API** - All AI models hosted here
- **Dependencies**: `replicate`, `python-dotenv`, `requests`, `Pillow`

## Pipeline (4 Steps)

### 1. Story Generation
**Model**: `google/gemini-2.5-flash`  
Converts theme into structured JSON with 3-6 scenes (characters, descriptions, motion prompts)

### 2. Image Generation
**Model**: `minimax/image-01`  
Creates individual character images and scene backgrounds

### 3. Scene Compositing  
**Model**: `flux-kontext-apps/multi-image-kontext-pro`  
Composites characters into scene backgrounds (handles multi-character scenes iteratively)

### 4. Video Generation
**Model**: `bytedance/seedance-1-pro`  
Generates 5-second video clips for each scene, then stitches them together

## Project Structure

video-story-generator/
├── .env # REPLICATE_API_TOKEN
├── requirements.txt
├── README.md
└── config/
  ├── prompts.json
└── data/
  ├── images/
  ├── scenes/
  ├── stories/
  ├── videos/
└── src/
  ├── config.py
  ├── utils.py
  ├── main.py
  ├── story_generator.py # Step 1
  ├── generate_images.py # Step 2
  ├── generate_scenes.py # Step 3
  ├── generate_video.py  # Step 4 

## Installation

1. **Clone repository**
git clone https://github.com/yourusername/replicateVideoGen.git
cd replicateVideoGen

2. **Install dependencies**
pip install -r requirements.txt

3. **Add environment variables**

Create `.env` file:
REPLICATE_API_TOKEN=your_replicate_token_here

## Usage

from src.generate_videos import generate_video

Generate video from theme
theme = "A magical forest adventure with talking animals"
video_path = generate_video(theme)

## Output Example

The story generator produces JSON like:
{
"characters": [
{"characterId": "char1", "name": "Luna", "characterPrompt": "..."}
],
"scenes": [
{
"sceneNumber": 1,
"sceneDescription": "...",
"audioText": "...",
"characterIds": ["char1"],
"settingPrompt": "...",
"motionPrompt": "...",
"durationSeconds": 5
}
]
}
