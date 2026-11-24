import { NextResponse } from 'next/server';
import { getReplicateClient, MODELS } from '@/lib/replicate';

export async function POST(req: Request) {
  try {
    const { theme, customToken } = await req.json();
    const promptTheme = theme || 'a solitary botanist uncovering a glowing flora sanctuary in an abandoned cyberpunk city';

    const promptText = `
Create a creative, engaging short story based on the theme: "${promptTheme}"
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

Return ONLY valid JSON in this structure:
{
  "characters": [{ "characterId": "char1", "name": "Name", "characterPrompt": "..." }],
  "scenes": [{ "sceneNumber": 1, "sceneDescription": "...", "audioText": "...", "characterIds": ["char1"], "characterContext": "...", "settingPrompt": "...", "startingSettingPrompt": "...", "endingSettingPrompt": "...", "motionPrompt": "...", "durationSeconds": 5 }]
}
`;

    const replicate = getReplicateClient(customToken);

    // Run Gemini model via Replicate
    const output = await replicate.run(
      MODELS.GEMINI as `${string}/${string}`,
      {
        input: {
          prompt: promptText
        }
      }
    );

    let rawText = '';
    if (Array.isArray(output)) {
      rawText = output.join('');
    } else if (typeof output === 'string') {
      rawText = output;
    } else {
      rawText = JSON.stringify(output);
    }

    // Clean markdown code blocks
    let cleaned = rawText.trim();
    if (cleaned.startsWith('```json')) cleaned = cleaned.slice(7);
    else if (cleaned.startsWith('```')) cleaned = cleaned.slice(3);
    if (cleaned.endsWith('```')) cleaned = cleaned.slice(0, -3);
    cleaned = cleaned.trim();

    const storyData = JSON.parse(cleaned);

    return NextResponse.json({
      success: true,
      story: storyData
    });
  } catch (error: any) {
    console.error('Story generation error:', error);
    return NextResponse.json(
      { success: false, error: error.message || 'Failed to generate story' },
      { status: 500 }
    );
  }
}
