# Day 25 — Model-Based Planner For Repo Assistant

**DRAFT — written retroactively from actual commits/tests, review and personalize before treating as final.**

**Goal:** Replace `repo_assistant.py`'s keyword-only router with a model-based planner (same upgrade `mock_loop.py` got on Day 19), so routing understands intent instead of relying on exact keyword matches.

---

## What Was Built

- Added `model_plan_action(intent, context="", history=None)` to `repo_assistant.py` — sends a system prompt listing the valid actions (`answer_question`, `check_git_status`) to Groq (`llama-3.1-8b-instant`, `temperature=0`), cleans the response (strips backticks/quotes), and validates it against `ALLOWED_ACTIONS`.
- Falls back to the existing rule-based `plan_action(query)` if: the model returns something invalid, or the Groq call itself raises an exception — same defensive pattern as `mock_loop.py`, never trusting the model blindly.
- Wired `__main__` to use `model_plan_action` instead of `plan_action` directly.

## Bugs Found And Fixed Along The Way

- First draft's system prompt still listed `mock_loop.py`'s old action set (`read_progress_files, summarize_status, check_git_status, ask_clarification`) — copy-pasted without updating, meaning the model could never return `answer_question` at all. Fixed to list the actual two actions this file has.
- `model_plan_action`'s signature required a `context` argument with no default, but it was called with only one argument — `TypeError`. Fixed by giving `context` a default value.

## Test Evidence

- `"tell me about my commits"` (no literal "git" or "status" keyword) → correctly routed to `check_git_status` via the model, not keyword luck.
- `"tell me about embeddings"` → correctly routed to `answer_question`, real cited answer returned.

## File Updated

- `projects/day-24-repo-assistant/repo_assistant.py`

## Key Learning

A model-based router needs the same fallback discipline as any other AI-in-the-loop system: validate its output against a known-safe set, and always have a non-AI fallback path ready for when it inevitably returns something unexpected.

## Next Step

Add a third tool (`read_progress_files`) to prove the router scales past two actions.
