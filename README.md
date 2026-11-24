# StoryForge — AI story-to-video pipeline

**StoryForge turns a one-line theme into an illustrated, animated short story.** Gemini writes a structured story, MiniMax paints the characters and settings, FLUX Kontext composites each character into its scene, and Seedance animates every scene into a video clip, all through Replicate.

The core idea is **structured continuity**: the story is a JSON document with stable character IDs, appearance prompts, setting prompts and motion prompts. Every stage reads that same document, so the same characters carry through from the first image to the last clip.

## Pipeline

```text
  --theme "space adventure"
            │
            ▼
 ┌─────────────────────┐   data/stories/story_output.json
 │ 1. Story  (Gemini)  │──► characters[] + scenes[]
 └─────────────────────┘
            │
            ▼
 ┌─────────────────────┐   data/images/char1.jpeg, scene_1.jpeg, ...
 │ 2. Images (MiniMax) │──► one portrait per character, one backdrop per scene
 └─────────────────────┘
            │
            ▼
 ┌─────────────────────┐   data/scenes/scene_1_scene.png, ...
 │ 3. Scenes (FLUX     │──► characters composited into each backdrop
 │    Kontext)         │
 └─────────────────────┘
            │
            ▼
 ┌─────────────────────┐   data/videos/scene_1.mp4, ...
 │ 4. Video (Seedance) │──► each composited scene animated into a clip
 └─────────────────────┘
```

| Stage | Script | Model | Output |
| --- | --- | --- | --- |
| Story | `src/story_generator.py` | `google/gemini-2.5-flash` | `data/stories/story_output.json` |
| Character & setting art | `src/generate_images.py` | `minimax/image-01` | `data/images/*.jpeg` |
| Scene compositing | `src/generate_scenes.py` | `flux-kontext-apps/multi-image-kontext-pro` | `data/scenes/scene_N_scene.png` |
| Video clips | `src/generate_video.py` | `bytedance/seedance-1-pro` | `data/videos/scene_N.mp4` + `scene_N_url.txt` |
| Orchestrator | `src/main.py` | — | runs all four stages in order |

## Model choices

- **Gemini 2.5 Flash** writes a 30–60 second story split into 3–6 scenes. It returns strict JSON: characters with detailed appearance prompts, and scenes with setting, start/end composition, motion and duration.
- **MiniMax Image-01** produces 16:9 character portraits and character-free scene backdrops, with prompt optimisation enabled.
- **FLUX Kontext multi-image (Pro)** takes a character image and a backdrop and blends them, guided by the scene description and character context. Scenes with several characters are built up one character at a time.
- **Seedance 1 Pro** animates each composited scene image (image-to-video) using the scene's motion and setting prompts, at 480p / 24 fps, in 5 or 10 second clips.

## Setup

**Requirements:** Python 3.10+ and a [Replicate](https://replicate.com) API token.

```bash
git clone https://github.com/vldzio/replicateVideoGen.git
cd replicateVideoGen
python -m venv .venv
# macOS/Linux:        source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file in the project root (it is already in `.gitignore`):

```env
REPLICATE_API_TOKEN=r8_your_token_here
```

Model IDs and output folders are configured in `src/config.py`.

## Usage

### Run the whole pipeline

```bash
python src/main.py --theme "a lighthouse keeper befriends a storm spirit"
```

Leave out `--theme` to be prompted for one; press Enter at the prompt to let Gemini choose. Add `--max-scenes N` to render video for only the first N scenes (handy for quick previews).

### Run stages individually

Each stage reads the previous stage's output from `data/`, so you can rerun or tweak any step on its own:

```bash
python src/story_generator.py --theme "underwater mystery"   # 1. story JSON
python src/generate_images.py                                 # 2. character + backdrop images
python src/generate_scenes.py                                 # 3. composited scenes
python src/generate_video.py --max-scenes 3                   # 4. clips (default: all scenes)
```

Run commands from the repository root.

## Project structure

```text
replicateVideoGen/
├── src/
│   ├── main.py              # orchestrator: story → images → scenes → video
│   ├── story_generator.py   # Gemini story JSON (optional --theme)
│   ├── generate_images.py   # MiniMax character & backdrop images
│   ├── generate_scenes.py   # FLUX Kontext character/scene compositing
│   ├── generate_video.py    # Seedance image-to-video clips per scene
│   ├── config.py            # model IDs, paths, .env loading
│   └── utils.py             # JSON and filename helpers
├── config/
│   └── prompts.json         # story prompt template
├── data/                    # sample outputs: stories/, images/, scenes/, videos/
├── requirements.txt
└── .env                     # your REPLICATE_API_TOKEN (not committed)
```

The `data/` folder ships with a sample story and its generated images, composited scenes and clips, so you can see the output format before running anything.

## Roadmap

- Stitch the per-scene clips into a single film with narration audio.
