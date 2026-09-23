# Day 31 — Evals For The Deployed Assistant

**Goal:** Prove the live `/ask` endpoint actually works reliably, not just that it responds — same idea as Day 16's RAG evals, applied to a real deployed API instead of a local script.

---

## What Was Built

- New project: `projects/day-31-deployed-evals/`.
- `eval_questions.json` — 10 real questions: 7 RAG questions grounded in content already confirmed present in `days/*.md` (temperature, RAG, embeddings, ChromaDB, Groq, FastAPI, the Ollama removal), plus 3 routing questions (`check_git_status`, `read_progress_files`, and one deliberately ambiguous phrasing — "tell me about my commits" — with no literal keyword, same test used in Day 25).
- `run_eval.py` — adapted from Day 16's harness, but rewritten to test a live HTTP API instead of calling a local function: sends each question via `requests.post` to `https://repo-assistant-api.onrender.com/ask`, checks whether an `expected_keyword` appears in the response (case-insensitive substring / word-overlap match, same logic as Day 16), and writes results to `eval_results.json`.

## A Real Limitation Found While Building This

The `/ask` endpoint's JSON response only contains `{"ok", "message"}` — it never reveals which action (`answer_question`, `check_git_status`, `read_progress_files`) actually ran. Unlike `mock_loop.py` (which explicitly logs `planner_source`/`action` per step), there's no way to directly verify routing correctness from the API response alone — only by inferring it from the message's shape (e.g. `"Git status: ..."` only ever comes from `check_git_status`). This is a real observability gap worth fixing later.

## Test Evidence

First run against the live URL: **9/10 passed (90%)**. The one failure ("why did the embedding step break when deployed") was a genuine retrieval bug, not a flaw in the eval — investigated fully in [Day 32](day-32-debugging-retrieval-failure.md).

## Key Learning

An eval harness testing a live deployed API needs different plumbing than one testing a local function (HTTP calls instead of direct calls, inferring internal state from output shape instead of reading it directly) — but the actual evaluation logic (keyword/word-overlap matching, pass/fail tracking, a results file) carries over almost unchanged from Day 16. The skill of "designing a test set with expected outcomes" transfers; only the mechanism for calling the system under test changes.

## Next Step

Investigate why the one failing question got a wrong answer — see [Day 32](day-32-debugging-retrieval-failure.md).
