# Day 19 — Real Planner + Real Tool Integration

**Goal:** Move from mock workflow loop to a controlled real planner/executor loop.

---

## What Was Built

- Added a real model planner path using Groq (`llama-3.1-8b-instant`) behind a feature flag.
- Kept deterministic fallback planner logic to preserve reliability.
- Added allowed-action guardrails so model output can only map to:
  - `read_progress_files`
  - `summarize_status`
  - `ask_clarification`
- Added real tool execution path behind a feature flag.
- Implemented safe file-based tool calls for:
  - Reading `progress.md` and `roadmap.md`
  - Producing a status summary from `progress.md`
- Preserved Day 18 safety controls:
  - max steps
  - retries
  - stop conditions
  - structured step logs

## Why This Matters

This is the first true planner/executor split:

1. Planner (LLM) suggests an action.
2. Guardrails constrain action space.
3. Executor runs only approved actions.
4. Loop logs and stop policies keep behavior controlled.

This pattern is the core of safe tool-using assistants.

## Testing Evidence

- Syntax validation passed: `python -m py_compile .\\mock_loop.py`
- Interactive run validated:
  - `progress`
  - `failonce summarize status`
  - `quit`
- Observed expected behavior:
  - completed actions accumulated
  - retry path handled transient fail simulation
  - loop stopped cleanly on user quit

## File Updated

- `projects/day-18-workflow-topics/mock_loop.py`

## Key Learning

Integrating a real LLM call is not enough. The bigger engineering value comes from constraints (allowed actions), fallback behavior, and observability. Those are what make an AI loop production-safe.

## Next Step

- Add one more real tool action (e.g., safe git status reader) and include action-confidence metadata in logs.
