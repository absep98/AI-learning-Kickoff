# Day 30 — Simple Frontend + Syncing Local RAG Coverage

**Goal:** Close two remaining gaps after Day 29's deployment: (1) the live app only had a raw JSON API, no real UI, and (2) the local RAG collection was stale, missing 13 days of newer notes.

---

## What Was Built

### 1. A real frontend at `/chat`
Added a `GET /chat` route in `main.py` returning a plain HTML page (inline string, no build step, no extra framework) — a text input, a button, and a small `fetch()` call to the existing `POST /ask` endpoint. Kept `/` unchanged as Render's lightweight health check endpoint. This turns the live deployment from "an API only a developer would test via Swagger" into an actual clickable product anyone can use.

### 2. Local RAG rebuilt to match the deployed version
Discovered the local `chroma_db` was stale — built once around Day 14-16 and never rebuilt since, because `_build_collection_if_empty()` only rebuilds when the collection is completely empty. Days 17-29 notes were missing from local retrieval entirely (questions about the planner, FastAPI, or deployment returned "No relevant notes found" locally, even though the *deployed* version — which rebuilds fresh on every Render redeploy — already had them). Fixed by deleting the local `chroma_db` folder and letting the self-healing logic rebuild it via the Hugging Face embedding API: now 27 files, 697 chunks, covering Days 1-29.

## Test Evidence

- Local: `answer_question("what is FastAPI and why did we deploy to render")` now returns a real, correct answer sourced from Day 27-29 notes (previously would have failed).
- Live: visited `https://repo-assistant-api.onrender.com/chat`, typed "what is temperature" into the input box, clicked "Ask," got a real rendered answer directly on the page — verified via an automated browser check, not just curl/PowerShell.
- Confirmed `/ask` still works correctly after the frontend addition (`check git status` → real git status from the deployed server).

## Files Updated

- `projects/day-27/awesome-project/main.py` (new `/chat` route)
- Local `projects/day-14-chromadb/chroma_db/` (rebuilt, not committed — gitignored)

## Key Learning

A self-healing "rebuild if empty" strategy only protects against the *complete absence* of data — it doesn't protect against *staleness*. The collection wasn't empty, so it silently never updated even as 13 days of new notes were added. Worth remembering for any cache/database that's lazily populated: "empty" and "outdated" are different failure modes and need different checks.

## Where This Leaves Repo Assistant

Live, public, with a real UI, answering from the full current set of learning notes — both locally and deployed. Next real step (not yet done): evals for the deployed `/ask` endpoint, to prove answer quality systematically rather than by spot-checking a handful of manual questions.
