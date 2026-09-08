# Day 22 — Conversation History In Planner Context

**Goal:** Give the model planner memory of the run so far, instead of deciding each step from a single isolated prompt.

---

## What Was Built

- `model_plan_action()` now takes an optional `history` argument (list of `{intent, action}` dicts from prior steps).
- Before sending the current intent, prior steps are replayed into the Groq chat messages as alternating `user`/`assistant` turns (`user`: past intent, `assistant`: past chosen action) — real conversational memory, not just a text blob appended to the prompt.
- `run_mock_loop()` now keeps a `history` list, appends `{intent, action}` after every step, and passes it into `model_plan_action(prompt, context, history=history)`.
- System prompt and allowed-action guardrails from Day 19/20 are unchanged — history only adds context, it doesn't expand what the planner is allowed to return.

## Test Evidence

Ran the loop with `progress`, then `whats git status`, then `quit`. Log written to `run_logs/run_20260624_162044.json`:

```json
{
  "stop_reason": "user quit",
  "completed_actions": ["read_progress_files", "check_git_status"],
  "steps": [
    { "step": 1, "intent": "progress", "action": "read_progress_files", "planner_source": "model", "retry_attempts": 1 },
    { "step": 2, "intent": "whats git status", "action": "check_git_status", "planner_source": "model", "retry_attempts": 1 },
    { "step": 3, "intent": "quit", "action": "none", "next_decision": "stop", "planner_source": "none" }
  ]
}
```

Both real steps resolved via `planner_source: model` (not fallback), confirming the model correctly picked distinct actions for two different intents in the same run while carrying prior turns in context.

## File Updated

- `projects/day-18-workflow-topics/mock_loop.py`

## Key Learning

Multi-step "memory" for an LLM planner isn't a special feature — it's just replaying prior turns as real chat messages instead of re-describing state in a single string. That's the same statelessness lesson from Day 6/8, applied now to an agent loop instead of a chatbot.

## Where This Leaves The Workflow Loop

With Day 18–22 combined, `mock_loop.py` now has: a real planner + real tool executor (Day 19), an added tool + decision metadata (Day 20), persisted run logs (Day 21), and planner memory across steps (Day 22). This satisfies Month 2 Option C's success signal — "build a controlled multi-step assistant workflow" — end to end.

## Next Step

- Decide between hardening this loop further (e.g. more tools, smarter stop conditions) or moving on to Month 2's main task: using AI day-to-day and shipping an actual small AI feature in a real app/product.
