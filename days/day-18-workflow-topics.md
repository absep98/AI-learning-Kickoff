# Day 18 — Workflow Topics (Month 2 Start)

**Goal:** Begin controlled multi-step assistant workflow design

---

## Day 18 Tasks

Define a conversation memory strategy for AI workflows.

### Deliverable

Write 5-8 bullet points answering:

1. What should be stored as persistent user memory?
2. What should stay session-only?
3. What should be repository-scoped?
4. What should never be stored?
5. When should memory be updated?

### My Memory Strategy (Completed)

- Persistent user memory stores stable user-specific preferences, working style, and explicit "remember this" instructions that should carry across sessions.
- Session memory stores temporary context for the current chat: current goal, in-progress decisions, and short-term patterns observed while solving the active task.
- Repository memory stores project-specific facts: codebase conventions, architecture choices, language/tooling patterns, and repo-level workflows.
- Never store secrets or sensitive data in memory (API keys, tokens, passwords, personal private data). Secrets should be loaded from environment files or secure secret management.
- Update memory when new stable structure appears (architecture or workflow changes), when repo conventions change, or when the user explicitly asks to remember/update something.
- Prefer minimal, high-signal memory entries and avoid noisy details that are unlikely to help future decisions.

### Success Signal

You can explain exactly which memory belongs in each scope without ambiguity.

---

## Why This First

Before tool loops and agent orchestration, memory boundaries prevent confusion, leakage, and noisy context.

---

## Tool-Calling Loop Rules

- Start a loop when a user request needs multiple dependent actions (for example: search, read, edit, verify) rather than a single direct response.
- Set a max step limit per run (for example 8 steps) to avoid runaway execution; if limit is reached, return progress and ask for continuation.
- Stop the loop when success criteria are met, when the user asks to stop/quit, when required input is missing, or when repeated failures make safe progress impossible.
- Retry failed tool calls up to 3 times only for transient issues (timeouts, temporary unavailability); do not retry unchanged calls for deterministic errors.
- Log each step with: user intent, tool/action taken, key input context used (files/attachments/history), result, and next decision.

## Example Run

- User intent: Check overall roadmap and progress status.
- Steps taken: Read progress.md and roadmap.md, extract completed items and pending items, then summarize.
- Stop reason: Required files were found and task objective was met.
- Logged output summary: Intent captured, 2 file reads executed, completion/pending list generated, final response delivered.

## Pseudocode: Controlled Tool-Calling Loop

```text
max_steps = 8
for step in 1..max_steps:
    intent = get_user_intent()
    if intent is empty: stop("missing input")

    context = load_context(session_history, attachments, allowed_memories)
    plan = model_plan_next_action(intent, context)

    result = execute_tool_with_retry(plan.tool, plan.args, retries=3)
    log_step(step, intent, plan, result)

    if result.meets_success_criteria: respond_and_stop(result.summary)
    if user_requested_stop(): stop("user quit")

respond_with_progress("step limit reached", collected_logs)
```

## Part 4: Runnable Mock Loop

- Input source: user prompt from terminal input.
- Max steps: 8.
- Retry count: 3 per tool call.
- Stop conditions: success, user quit, step limit reached.
- Log fields: step, intent, action, result, next decision.
- Final output summary: completed actions, pending items, stop reason.

## Part 5: Implementation Snapshot (Completed)

- Implemented runnable prototype in `projects/day-18-workflow-topics/mock_loop.py`.
- Added `StepLog` dataclass for structured per-step observability.
- Added action planner (`plan_action`) for intent-to-action routing.
- Added retry wrapper (`execute_with_retry`) with 3-attempt transient failure handling.
- Added configurable mode toggle (`ONE_SHOT_MODE`) to switch between one-shot and multi-turn behavior.
- Added final reporting block with completed actions, pending items, stop reason, and detailed step logs.

## Test Evidence

- Syntax validation passed via `python -m py_compile .\\mock_loop.py`.
- Multi-turn run validated with sequence: `progress` -> `failonce summarize status` -> `missing input` -> `quit`.
- Observed expected outcome: accumulated completed actions across turns and terminated with `stop reason: user quit`.
