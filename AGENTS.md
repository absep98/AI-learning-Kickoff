# Repository Guidelines

This is a personal daily-learning journal for AI/LLM concepts, not a packaged application. Each day produces a markdown writeup plus, often, a standalone Python script. There is no shared build system, test suite, or linter — treat each `projects/day-*` folder as an independent script.

## Project Structure & Module Organization

- `days/day-NN-topic.md` — the daily writeup (concepts learned, corrections, findings). Read the relevant day's note before touching its matching project.
- `projects/day-NN-topic/` — the runnable code for that day, usually a single script (e.g. `rag_v2.py`, `mock_loop.py`) run directly with `python`. Scripts are not part of a package and don't import from each other.
- `progress.md` / `roadmap.md` — living trackers of what's done and planned next; update these when a day's work lands (see recent commits for the pattern).
- `cheatsheet.md` — running glossary of concepts across all days.
- `archive/` — superseded planning docs (e.g. `plan-v0.md`).
- `Demos/` — small standalone example scripts (`embedding_demo.py`, `tokenize_demo.py`) unrelated to the day-by-day track.
- `.env` (gitignored) holds API keys — currently `GROQ_API_KEY` and `GOOGLE_API_KEY`. Scripts load it via `python-dotenv`, often with a hardcoded absolute path (see `projects/day-18-workflow-topics/mock_loop.py`).

The most actively evolving project is `projects/day-18-workflow-topics/mock_loop.py`: a tool-calling agent loop with a model-based planner (Groq `llama-3.1-8b-instant`), retry logic, and per-run JSON logs written to `run_logs/`.

## Build, Test, and Development Commands

There is no root-level dependency file or task runner. Only `projects/day-17-git-ai-summary/requirements.txt` exists (`groq`, `python-dotenv`); other scripts assume packages (`groq`, `python-dotenv`, `chromadb`, `google-generativeai`, etc.) are already installed in the active environment.

Run any day's script directly, from the repo root, e.g.:
```
python projects/day-18-workflow-topics/mock_loop.py
python projects/day-17-git-ai-summary/git_ai_summary.py [unstaged|staged|both]
python projects/day-16-rag-evals/run_eval.py
```
There are no automated tests. `day-16-rag-evals/run_eval.py` is a manual eval harness (compares answers against `eval_questions.json`, writes `eval_results.json`) — the closest thing to a test suite in this repo.

## Coding Style & Naming Conventions

No linter or formatter is configured. Follow the existing style in `projects/*/`: 4-space indentation, `snake_case` functions, module-level constants in `UPPER_CASE` (e.g. `MAX_STEPS`, `ALLOWED_ACTIONS`), and `@dataclass` for structured records (e.g. `StepLog`). Scripts are single-file and procedural — no packages, no `__init__.py`, no shared internal imports.

## Commit & Pull Request Guidelines

Commits follow `dayNN: short imperative description` (e.g. `day21: persist step logs to timestamped json after each run`), occasionally `Day NN: Description` (older commits) or with a `/` for two related days (`day16/day17: ...`). A day's commit typically touches its `days/day-NN-*.md` note, `progress.md`, `roadmap.md`, and the corresponding `projects/day-NN-*/` code together. There is no PR template or CI; this repo is pushed to directly.
