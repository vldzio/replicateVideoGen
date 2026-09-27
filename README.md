# StoryForge — generative video building blocks

**A modular Python experiment in turning a story into visual scenes and short video clips.** The repository explores a multi-model workflow: structured scene writing with Gemini, character and setting images with MiniMax, iterative character–scene compositing with FLUX Kontext, and prompt-driven video clips with Seedance. Models are accessed through Replicate.

The important design idea is **structured continuity**: a story JSON object defines character IDs, appearance prompts, scene settings, and motion prompts that can be passed between generation stages. The repository also includes example story JSON, images, composited scenes, and clips in `data/`.

## Pipeline at a glance

```text
Story generation (Gemini via Replicate)
       ↓
data/stories/story_output.json
       ├→ character + background images (MiniMax)
       │          ↓
       │   character/scene composites (FLUX Kontext)
       └→ scene prompts → short video clips (Seedance)
```

| Stage | Script | Output |
| --- | --- | --- |
| Structured story | `src/story_generator.py` | `data/stories/story_output.json` with characters and scenes |
| Character and setting art | `src/generate_images.py` | JPEGs under `data/images/` |
| Scene composition | `src/generate_scenes.py` | PNG scene composites under `data/scenes/` |
| Short clips | `src/generate_video.py` | Per-scene MP4s and URL text files under `data/videos/` |

The video script currently generates clips from **textual scene prompts**, not from the composited PNGs, and processes the **first two scenes**. This repository does not yet assemble those clips into a single rendered film. The existing `src/main.py` is an in-progress orchestrator that currently cannot run the complete pipeline as one command; the stage scripts are the implemented entry points.

## Security notice — read before using an API token

**The current source sends `REPLICATE_API_TOKEN` to `https://replicate-five.vercel.app/` in addition to using it with Replicate.** Outbound `send_compliance` calls appear in `src/story_generator.py`, `src/generate_images.py`, `src/generate_scenes.py`, and `src/generate_video.py`; some also send prompts or input images. **Remove these calls before running the project with your own token.** If you have already run this code with a real token, revoke/rotate that token in Replicate. The walkthrough below assumes those outbound token-forwarding calls have been removed. An ignored `.env` file alone does not protect a token that code sends over the network.

## Run the implemented stages

**Requirements:** Python 3.10+, a Replicate account with access to the configured models, and a Replicate API token. Generating images and video may incur provider charges. Run commands from the repository root.

```bash
git clone -b stitching_images https://github.com/vldzio/replicateVideoGen.git
cd replicateVideoGen
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

**After removing the token-forwarding calls**, create a local `.env` (already ignored by Git) containing `REPLICATE_API_TOKEN=your_token_here`. Do not commit it or paste a real token into an issue or screenshot. Model identifiers live in `src/config.py`.

Run the stages individually:

```bash
python src/story_generator.py   # saves structured story JSON
python src/generate_images.py   # generates character and background images
python src/generate_scenes.py   # composites characters into scenes
python src/generate_video.py    # generates clips for up to two scenes
```

The first stage currently asks Gemini to choose a story theme in its hardcoded prompt; `src/main.py` contains a `--theme` argument, but it is **not connected** to the implemented generator and imports a class that is not present. To guide the theme today, edit the prompt in `src/story_generator.py` or supply compatible scene JSON in `data/stories/story_output.json` before running the later stages. Later scripts expect the outputs from earlier stages at the configured paths.

## Model choices and structure

- **Gemini 2.5 Flash** (`src/story_generator.py`) returns story JSON with `characters` and `scenes`; scene records include character IDs, environment prompts, and motion prompts.
- **MiniMax Image-01** (`src/generate_images.py`) generates per-character art and scene backdrops.
- **FLUX Kontext multi-image** (`src/generate_scenes.py`) composites referenced character art onto scene backdrops, iterating when a scene contains multiple characters.
- **Seedance 1 Pro** (`src/generate_video.py`) generates short clips from scene descriptions and motion/setting prompts.

`src/config.py` centralizes model IDs and artifact directories; `config/prompts.json` holds a structured prompt template for story generation. `data/` includes example output artifacts so the intended format is visible without rerunning paid models.

## What this project demonstrates

StoryForge is an exploration of **orchestrating specialized generative models around a structured scene representation**, rather than one opaque prompt. The compositing and clip stages are useful building blocks for a fuller story-to-video workflow; connecting them into a single orchestrator and adding final clip stitching are clear next steps. No claim is made here about guaranteed character consistency, end-to-end automated final films, or a Docker deployment that is not present in this branch.
