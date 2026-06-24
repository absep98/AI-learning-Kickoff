# Day 20 — Decision Metadata and Extended Tool Actions

**Goal:** Expand the controlled loop with a new tool action and decision metadata in logs.

---

## What Was Built

- Added `check_git_status` as a safe real tool action using `git status --short`.
- Added `planner_source` field to `StepLog`: records whether model or fallback planner was used.
- Added `retry_attempts` field to `StepLog`: records how many attempts the tool needed.
- Updated `execute_with_retry` to return attempt count in response dict.
- Updated model planner system prompt to include `check_git_status`.
- Updated fallback `plan_action` to route `git/commit/branch` keywords to `check_git_status`.

## Test Evidence

Interactive run with: `git status`, `failonce summarize status`, `quit`

```
step=1 | intent='git status' | action=check_git_status | result=Git status: 1 changed file(s) | next_decision=continue | planner=model | retries=1
step=2 | intent='failonce summarize status' | action=summarize_status | result=Status summary: Day 20 (next) | ... | next_decision=continue | planner=model | retries=2
step=3 | intent='quit' | action=none | result=user quit | next_decision=stop | planner=none | retries=0
```

- `retries=2` on step 2 confirms retry policy working correctly after simulated first-attempt failure.
- `planner=model` confirms real Groq planner was used on steps 1 and 2.

## Key Learnings

- Observability in agent logs tells you not just what happened, but how it was decided (model vs fallback) and how reliably (retry count).
- Adding metadata to each log step makes the difference between a debug tool and a production-quality agent trace.
