# StoryForge (replicateVideoGen) - project context

## What this is
Story -> images -> scene composites -> short video clips pipeline. Python CLI (`src/`) plus a Next.js 14 web app (`web/`). This branch (`demo-ready`) adds a hosted demo:

```text
Browser (Vercel, root dir web/) --story--> Hugging Face Space `demo_api/` (limits, BYO key, LangSmith)
                                              -> private FreeLLMAPI gateway (127.0.0.1:3001, same container) -> free-tier LLMs
        \--images/video--> Next API routes (web/src/app/api/*) -> Replicate, ONLY with the visitor's own Replicate token
```

The branch is based on `feat/vercel-demoable-app` (not `main`). PR: demo-ready -> `stitching_images` (the repo default branch).

## Layout
- `demo_api/app.py` - `POST /story` (same prompt/JSON shape as `web/src/app/api/story/generate/route.ts`), `demo_api/{llm,base,guard,gateway}.py` shared demo plumbing.
- `web/src/app/page.tsx` - UI: "Write story (free)" button, `fetchStory()`, optional LLM key in the key dialog (sessionStorage only).
- `web/src/lib/{replicate,demoData}.ts` - Replicate client + bundled sample showcase (`web/public/demo/`). NOTE: `lib/` was previously swallowed by a Python `.gitignore` rule; the ignore is now anchored to `/lib/`.
- `deploy/space/` - Dockerfile, start.sh, README (HF Space recipe). `src/` is the original Python pipeline.

## Run and test
- API tests: `python -m venv .venv && .venv\Scripts\pip install -r demo_api/requirements.txt pytest && .venv\Scripts\pytest tests`
- Web: `cd web && npm install && npm run build`; local story flow: run `uvicorn demo_api.app:app --port 8170` and `NEXT_PUBLIC_DEMO_API_URL=http://127.0.0.1:8170 npm run dev`.

## Rules
- Never hard-code LLM output; the Preset Showcase is real pre-generated media and must stay labelled as a sample.
- Never send tokens anywhere except Replicate (the old Python code leaked `REPLICATE_API_TOKEN` to a third party; it is removed - do not reintroduce `send_compliance`-style calls).
- Rate limit client IP = LAST `X-Forwarded-For` entry (earlier ones are spoofable). Do not log API keys.

## Deploy facts
- Space `storyforge-demo-api`, LangSmith project `storyforge-demo`, Vercel root dir `web`, env var `NEXT_PUBLIC_DEMO_API_URL` = the Space URL.
- Space secrets: `ENCRYPTION_KEY` (64 hex), `FREEAPI_CONFIG_JSON` (provider keys), `LANGSMITH_API_KEY`, `UPSTASH_REDIS_REST_URL/TOKEN`; optional `CORS_ORIGINS`, `RL_PER_IP_DAILY`, `RL_GLOBAL_DAILY`.
- The Space Dockerfile clones this repo's `demo-ready` branch (build arg `REF`).
- Steps: `hf auth login`, `vercel login`, create the Space from `deploy/space/`, set the secrets, then `cd web && vercel deploy --prod --yes --build-env NEXT_PUBLIC_DEMO_API_URL=<space url>`.

## Status
Verified: 4 API tests pass, `next build` passes, UI checked in a browser. NOT verified: Space Docker build, real provider calls, Replicate media steps with a real token, live Vercel deploy.
