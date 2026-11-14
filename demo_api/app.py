"""StoryForge demo API: POST /story - the LLM writes the structured multi-scene story.

Same prompt and JSON structure as web/src/app/api/story/generate/route.ts and src/story_generator.py,
but served through the private FreeLLMAPI gateway (traced in LangSmith) so visitors need no Replicate
token for the story step. Image and video generation stay on Replicate with the visitor's own token.
"""
from __future__ import annotations

import os

os.environ.setdefault("DEMO_PROJECT", "storyforge")
os.environ.setdefault("LANGSMITH_PROJECT", "storyforge-demo")

from fastapi import Request  # noqa: E402

from . import llm  # noqa: E402
from .base import create_app, guarded  # noqa: E402

app = create_app("StoryForge demo API")

DEFAULT_THEME = "a solitary botanist uncovering a glowing flora sanctuary in an abandoned cyberpunk city"

PROMPT = """Create a creative, engaging short story based on the theme: "{theme}"
Design the story to fit within a 30 to 60 second video duration and break it down into 2 to 4 distinct scenes.

Return a JSON object with TWO main sections:

1. "characters": An array of all unique characters in the story (1 or 2 characters). For each character, provide:
- characterId: A unique identifier (e.g., "char1", "char2")
- name: The character's name
- characterPrompt: A highly detailed text prompt describing the character's appearance, clothing, age, distinctive features, hair, eyes, and overall visual style.

2. "scenes": An array of scenes. For each scene, provide:
- sceneNumber: The position of the scene in the story
- sceneDescription: A vivid and concise description of the scene's visuals and actions
- audioText: Creative text for background audio or narration
- characterIds: An array of character IDs that appear in this scene
- characterContext: Brief description of what the character(s) are doing in this specific scene
- settingPrompt: A detailed text prompt describing ONLY the environment, location, lighting, mood, and atmosphere without characters.
- startingSettingPrompt: Description of the setting at the start of the scene
- endingSettingPrompt: Description of the setting at the end of the scene
- motionPrompt: Description of animation, camera movement, or visual dynamics
- durationSeconds: Suggested duration in seconds (5 to 10)
"""

STORY_SCHEMA = {
    "type": "object",
    "properties": {
        "characters": {
            "type": "array",
            "minItems": 1,
            "maxItems": 3,
            "items": {
                "type": "object",
                "properties": {"characterId": {"type": "string"}, "name": {"type": "string"}, "characterPrompt": {"type": "string"}},
                "required": ["characterId", "name", "characterPrompt"],
            },
        },
        "scenes": {
            "type": "array",
            "minItems": 2,
            "maxItems": 5,
            "items": {
                "type": "object",
                "properties": {
                    "sceneNumber": {"type": "integer"},
                    "sceneDescription": {"type": "string"},
                    "audioText": {"type": "string"},
                    "characterIds": {"type": "array", "items": {"type": "string"}},
                    "characterContext": {"type": "string"},
                    "settingPrompt": {"type": "string"},
                    "startingSettingPrompt": {"type": "string"},
                    "endingSettingPrompt": {"type": "string"},
                    "motionPrompt": {"type": "string"},
                    "durationSeconds": {"type": "number"},
                },
                "required": ["sceneNumber", "sceneDescription", "characterIds", "settingPrompt", "durationSeconds"],
            },
        },
    },
    "required": ["characters", "scenes"],
}


async def _body(req: Request) -> dict:
    try:
        data = await req.json()
        return data if isinstance(data, dict) else {}
    except Exception:  # noqa: BLE001
        return {}


@app.post("/story")
async def story(req: Request):
    body = await _body(req)
    theme = str(body.get("theme") or "").strip()[:240] or DEFAULT_THEME

    def run():
        system = "You are a screenwriter producing structured JSON for an automated image/video pipeline."
        out = llm.chat_json(
            system, PROMPT.format(theme=theme.replace('"', "'")), schema=STORY_SCHEMA, temperature=0.8, max_tokens=3500,
            metadata={"route": "story"},
        )
        return {"success": True, "story": out}

    return await guarded(req, 2, run, name="storyforge.story")
