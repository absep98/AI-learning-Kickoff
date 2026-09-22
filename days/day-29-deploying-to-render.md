# Day 29 — Deploying Repo Assistant Live On Render

**Goal:** Actually deploy `assistant.py`/`main.py` to a real server, getting a public URL — the final step of Month 2's "ship an actual AI feature in a real app" goal.

---

## What Was Built

- Created a Render Web Service (`repo-assistant-api`), connected to the `AI-learning-Kickoff` GitHub repo, Root Directory set to `projects/day-27/awesome-project`.
- Build command: `pip install -r requirements.txt`. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`.
- Set `GROQ_API_KEY`, `HF_TOKEN`, and `REPO_ROOT=/opt/render/project/src` as environment variables in Render's dashboard.

## Three Real Blockers Hit And Fixed, In Order

**1. `requirements.txt` was never committed to git.**
Generated it locally with `uv export`, but it was untracked — Render's clone of the repo simply didn't have it, so the very first build failed with `Could not open requirements file`. Fixed by actually committing it.

**2. The default PyTorch install pulled multi-GB NVIDIA/CUDA packages.**
`uv export` resolved GPU-enabled `torch` by default, adding ~15 `nvidia-*`/`cuda-*` packages completely unnecessary on Render's CPU-only free tier. Fixed by adding `--extra-index-url https://download.pytorch.org/whl/cpu` to `requirements.txt` and manually stripping the CUDA-specific lines.

**3. The ChromaDB collection didn't exist on the fresh server — crashed on import.**
`chroma_db/` (the actual embedded-notes database) is gitignored and only ever existed on my laptop. On Render, `client.get_collection(name="ai_notes")` failed immediately because the collection was empty, crashing the whole app *before* `uvicorn` could bind to a port — which is why Render's logs just showed "No open ports detected" forever, with no other clue. Fixed by making the collection **self-healing**: `_build_collection_if_empty()` checks `collection.count()`, and if empty, rebuilds it from `days/*.md` (already in git) using the same embedding function used everywhere else.

**4. `sentence-transformers`/`torch` caused an actual out-of-memory crash.**
Even after fixing #3, the deploy failed again — this time Render's logs explicitly said `Out of memory (used over 512Mi)`. Loading `torch` + `transformers` alone uses 300-500MB, and embedding ~624 note chunks in one batch pushed it over the free tier's 512MB limit. Since paying for more RAM wasn't an option, the real fix was removing the heavy local ML libraries entirely: switched to **Hugging Face's hosted Inference API** (`huggingface_hub`'s `InferenceClient.feature_extraction()`) for embeddings — no `torch`, no `transformers`, no local model loaded at all. Confirmed the API returns identical 384-dim vectors for the exact same model (`sentence-transformers/all-MiniLM-L6-v2`), just computed remotely instead of in-process.

Removing `sentence-transformers` also dropped the dependency count from 122 to 86 packages and eliminated the multi-GB `torch` download from every build.

## Test Evidence

All 3 actions verified working against the real live URL (`https://repo-assistant-api.onrender.com`), not just locally:
- `POST /ask {"text": "what is temperature"}` → real, cited RAG answer.
- `POST /ask {"text": "check git status"}` → `"Git status: 1 changed file(s)"` (a real `git status` ran on Render's actual cloned copy of the repo).
- `POST /ask {"text": "what day am i on"}` → real `progress.md` content, read from the server's own copy of the repo.

## Key Learning

The deployment errors weren't random — each one traced back to something that quietly worked locally because it depended on the local machine (an ignored file, unlimited local RAM, or the assumption that a full ML stack is "free" to load). None of that is true on someone else's server. "It works on my machine" hides real assumptions that only surface once code has to run somewhere else — and each fix here (git-tracking a file, checking memory constraints, choosing a hosted API over a local model) is a genuinely transferable production-engineering skill, not just a workaround.

## File Updated

- `projects/day-27/awesome-project/assistant.py`
- `projects/day-27/awesome-project/requirements.txt`

## Where This Leaves Month 2

The success signal is met: a real AI feature (RAG + tool routing) is live, public, and demoable — not a local script only I can run. Next decision: keep extending this deployed feature (more tools, a simple frontend), or move on to a new focus area.
