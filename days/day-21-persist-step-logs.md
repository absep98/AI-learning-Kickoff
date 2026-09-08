# Day 21 — Persist Step Logs To File

**Goal:** Stop losing run history when the terminal closes — write each run's step logs to disk.

---

## What Was Built

- Added `persist_logs()` to `mock_loop.py`: builds a JSON payload (`timestamp`, `stop_reason`, `completed_actions`, `steps`) and writes it to `projects/day-18-workflow-topics/run_logs/run_<YYYYMMDD_HHMMSS>.json`.
- `run_logs/` is created on demand (`mkdir(exist_ok=True)`) and gitignored — logs are local run artifacts, not tracked history.
- Step logs (`StepLog` dataclasses) are serialized with `dataclasses.asdict`.
- Removed "persist logs" from the `pending_items` list printed at the end of a run, since it's now implemented.
- `persist_logs()` runs unconditionally at the end of `run_mock_loop()`, after the summary is printed.

## Test Evidence

Ran the loop with `progress` then `quit`. Log file written to `run_logs/run_20260624_120732.json`:

```json
{
  "timestamp": "20260624_120732",
  "stop_reason": "user quit",
  "completed_actions": ["read_progress_files"],
  "steps": [
    {
      "step": 1,
      "intent": "progress",
      "action": "read_progress_files",
      "result": "Read progress.md (27297 chars) and roadmap.md (17522 chars)",
      "next_decision": "continue",
      "planner_source": "model",
      "retry_attempts": 1
    },
    {
      "step": 2,
      "intent": "quit",
      "action": "none",
      "result": "user quit",
      "next_decision": "stop",
      "planner_source": "none",
      "retry_attempts": 0
    }
  ]
}
```

Confirms the full step trace (including planner source and retry counts from Day 20) survives after the process exits.

## File Updated

- `projects/day-18-workflow-topics/mock_loop.py`
- `projects/day-18-workflow-topics/.gitignore` (added to keep `run_logs/` out of git)

## Key Learning

A console trace disappears the moment the terminal scrolls or closes. Writing the same structured log to a timestamped file turns each run into a reviewable artifact — the first real step toward treating this loop as something debuggable over time, not just a live demo.

## Next Step

- Give the model planner memory of earlier steps in the same run, so decisions aren't made intent-by-intent in isolation.
