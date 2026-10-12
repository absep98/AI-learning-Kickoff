# Day 39 — User Feedback Loop (👍/👎)

**Goal:** Section 6's "User feedback loops" checklist item — capture a simple quality signal per answer instead of relying only on manual spot-checks.

---

## What Was Built

- `/ask` now generates a `uuid.uuid4()` identifier per response (`answer_id`), returned alongside the answer.
- A new `POST /feedback` endpoint accepting `{answer_id, vote}`, appending one JSON line (`answer_id`, `vote`, `timestamp`) to `feedback_log.jsonl` — same append-only, structured-logging pattern as Day 21's `run_logs/`.
- `/chat`'s frontend: two new buttons (👍/👎), wired to remember the current `answer_id` after each question and POST it with a vote on click.

**Storage decision, and why:** considered an in-memory dict (like the Day 37 cache / Day 38 rate limiter), but rejected it here — losing a cache or rate-limit counter on restart is harmless, but silently losing collected feedback defeats the entire point of building this. A JSON-lines file is the right middle ground: simple enough to build cleanly, and structurally identical to what a real logging pipeline does before a database enters the picture. Same honest caveat as `chroma_db/`: Render's ephemeral disk means this file is lost on every redeploy — fine for a personal project, explicitly documented rather than ignored.

## Real Mistakes Made Building It

1. `time.Now()` instead of `time.time()` — the exact same capitalization mistake as Day 38's rate limiter, caught the same way (by actually running it).
2. `json.dumps(fd)` called before ever adding `import json`.
3. A JavaScript structural bug: `sendFeedback()`'s entire function definition got pasted *inside* the parentheses of `input.addEventListener("keydown", ...)` instead of as its own separate function — a stray orphaned `)` was the tell. This would have silently broken the entire `<script>` block (including the original Ask button), not just the new feature.
4. The two new buttons were never actually wired to call `sendFeedback()` on the first pass — the function existed but nothing invoked it.

## An Unrelated Blocker Hit While Testing

Testing RAG questions (`"what is temperature"`) 500'd — not a bug in today's work. This is the same root cause as Day 38's production outage: Hugging Face's Inference API is still out of free credits. Day 38 only made the **startup** collection-rebuild resilient to this; it never addressed that **every single RAG question** also calls `embed()` to vectorize the query, which hits the same broken API. Confirmed by testing with a tool-routed question ("check git status") instead — that path doesn't touch embeddings at all, and feedback worked end-to-end, both locally and live, with a real `answer_id`.

**Deliberately not fixed today.** Restoring RAG requires either paying for HF credits or switching embedding providers (a real chunk of engineering work on its own, especially since running embeddings locally was already ruled out back on Day 28/29 — it OOM-crashed Render's 512MB free tier). Decided to ship the feedback feature now (it's fully correct and works for every question type; RAG answers will work the moment HF is restored, with zero code changes needed) and track the HF outage as its own separate, future task instead of rushing an unrelated fix into this session.

## Test Evidence

- Confirmed locally: asked a tool-routed question, clicked 👍, found the real `answer_id` (not a placeholder) correctly logged in `feedback_log.jsonl` with vote and timestamp.
- Confirmed live: same flow against `https://repo-assistant-api.onrender.com` — real `answer_id` returned from `/ask`, successfully submitted to `/feedback`, `{"ok": "true"}` returned.

## Key Learning

A feature can be fully correct and still only partially useful if an unrelated dependency is down — the honest move was separating "is this feature built right" (yes, verified two ways) from "is the thing it's meant to measure currently working" (no, for RAG specifically, and that's a different, already-tracked problem). Bundling an unrelated infra fix into today's work would have blurred what was actually accomplished.
