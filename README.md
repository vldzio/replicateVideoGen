# StoryForge — Generative AI Video Storyboard & Reel Pipeline

StoryForge transforms a high-level creative prompt into an episodic, multi-scene video reel with consistent character appearance and structured continuity across scenes.

Deployable on **Vercel** with a Next.js web application and interactive studio interface, as well as a standalone Python CLI pipeline.

---

## 🚀 Architecture & Pipeline

```
Story Prompt / Theme
       ↓
[1] Gemini 2.5 Flash (via Replicate)
    Structured JSON Screenplay: Characters, Setting Prompts, Dialogue, Motion
       ↓
[2] MiniMax Image-01 (via Replicate)
    Character Portraits & Environment Plates
       ↓
[3] FLUX Kontext Multi-Image (via Replicate)
    Seamless Character + Scene Compositing
       ↓
[4] ByteDance Seedance-1-Pro (via Replicate)
    Temporal Motion Video Clip Synthesis
       ↓
[5] Cinematic Reel Assembly & Player
```

---

## ⚡ Web App & Vercel Deployment (`/web`)

The repository includes a modern Next.js 14 App Router dashboard located in the [`web/`](./web) directory.

### Key Features:
* **Interactive Prompt Studio:** Generate multi-character, multi-scene storyboards on the fly.
* **Non-blocking Serverless Architecture:** Built specifically for Vercel timeouts using asynchronous prediction polling endpoints (`/api/predictions/[id]`).
* **BYOK (Bring Your Own Key):** Securely supply your own Replicate API token in the UI or via environment variables.
* **Preset Showcase Mode:** Instantly demo pre-rendered stories, stitched scenes, and video reels with zero API latency or token cost.
* **Cinematic Reel Player:** Interactive continuous player with automated audioText subtitles and per-scene scrubbing.

### Deploying to Vercel:
1. Push this repository to GitHub or import it into Vercel.
2. Set the **Root Directory** in Vercel project settings to `web`.
3. Add the environment variable:
   * `REPLICATE_API_TOKEN` = `your_replicate_api_token` (optional if users use the in-app modal).
4. Click **Deploy**.

To run locally:
```bash
cd web
npm install
npm run dev
```

---

## 💻 Python CLI Orchestrator (`/src`)

The Python CLI pipeline runs the end-to-end multi-stage process from your terminal:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
echo "REPLICATE_API_TOKEN=your_token_here" > .env

# 3. Run full orchestrated pipeline
python -m src.main --theme "cyberpunk detective uncovering a neon greenhouse"
```

### Security & Privacy Notice
All telemetry and token-forwarding calls (`send_compliance`) to external endpoints have been removed. API tokens are strictly utilized for direct communication with the official Replicate API.

## Live demo architecture

```text
Browser (Vercel, web/) --story--> Hugging Face Space: demo_api (limits, BYO key, LangSmith) -> private FreeLLMAPI gateway -> free-tier LLMs
        |
        +--images/video--> Next.js API routes -> Replicate (visitor's own token)
```

* **Story**: written live by an LLM through `demo_api/` (`POST /story`, same prompt and JSON structure as the pipeline, schema-validated). No token needed; small daily allowance per visitor, or bring your own OpenAI-compatible key in the key dialog. Every call is traced to LangSmith (`storyforge-demo`).
* **Images / video**: Replicate models cost money, so they only run with the visitor's own Replicate token. The **Preset Showcase** shows the repo's real pre-generated images and clips, clearly labelled as a sample.
* **Deploy**: Space recipe in [`deploy/space/`](deploy/space); Vercel project root `web/` with `NEXT_PUBLIC_DEMO_API_URL` set to the Space URL. Tests: `pip install -r demo_api/requirements.txt pytest && pytest tests`.
