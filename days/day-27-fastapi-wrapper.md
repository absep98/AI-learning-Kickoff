# Day 27 — Wrapping Repo Assistant In A FastAPI Web API

**DRAFT — written retroactively from actual commits/tests, review and personalize before treating as final.**

**Goal:** Turn `repo_assistant.py` (a CLI-only script only I can run) into a real, deployable web feature — the actual "ship an AI feature in a real app" milestone for Month 2, chosen over Streamlit for the backend/API engineering skill gap it closes (per `roadmap.md`'s own target profile: "Build normal production software... APIs").

---

## What Was Built

- New project: `projects/day-27/awesome-project/` (a `uv`-managed Python project, first time using `uv` instead of pip in this repo).
- Learned FastAPI fundamentals from scratch: path parameters (`/greet-path/{name}`) vs query parameters (`/greet-query?name=...`) vs POST request bodies validated with Pydantic `BaseModel`.
- `assistant.py` — ported all of `repo_assistant.py`'s logic (`retrieve_chunks`, `answer_question`, `check_git_status`, `read_progress_files`, `plan_action`, `model_plan_action`) into this new project, one function at a time, testing each via `uv run python assistant.py` before wiring it into the API.
- `main.py` — a `POST /ask` endpoint accepting `{"text": "..."}`, routing through `model_plan_action` to the correct function, same if/elif pattern as `repo_assistant.py`'s CLI loop.
- Made `REPO_ROOT` and the ChromaDB path environment-variable-configurable (`os.getenv(key, default)`, falling back to the existing hardcoded paths) — first step toward deployment, since a cloud server won't have `C:\learning\aithings` at all.

## Test Evidence

- All 3 actions verified working through live HTTP requests via FastAPI's auto-generated `/docs` (Swagger UI), not just the CLI:
  - `{"text": "what is temperature"}` → real cited RAG answer.
  - `{"text": "check git status"}` → `"Git status: 3 changed file(s)"`.
  - `{"text": "what day am i on"}` → real `progress.md` content.
- Confirmed the env-var path changes didn't break anything (same test re-run after each change, `Invoke-RestMethod` used to verify directly).

## Bugs Fixed Along The Way

- `os.getenv(key, default)` — the default must go **inside** `getenv()`'s parentheses, not as a second argument to `Path()`. Got this wrong twice before it was correct (`Path(os.getenv("REPO_ROOT"), r"C:\...")` is invalid — `Path()` joins path segments, it doesn't take a fallback default).
- Env var name typo (`REPo_ROOT` vs `REPO_ROOT`) — env var lookups are case-sensitive.

## File Created

- `projects/day-27/awesome-project/main.py`
- `projects/day-27/awesome-project/assistant.py`

## Key Learning

A CLI prototype and a deployable API are architecturally different things, even when the underlying logic is identical — the API needs its own project boundary (so deployment only needs one self-contained folder), environment-based config instead of hardcoded absolute paths, and a request/response contract (Pydantic models) instead of free-form `input()`/`print()`.

## Remaining Blocker Before Real Deployment

`retrieve_chunks()`'s embedding call depends on local Ollama (`http://localhost:11434`), which will not exist on a deployed server. This needs to be solved (switch to a hosted embedding API and re-embed the notes corpus) before this can actually go live.

## Next Step

Decide: solve the Ollama/embedding deployment blocker now, or pause deployment work and revisit later.
