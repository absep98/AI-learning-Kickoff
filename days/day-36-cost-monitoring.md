# Day 36 — Cost Monitoring (And An Accidental Bug Find)

**Goal:** Next open item in the roadmap's "AI Product Engineering" checklist — measure real $ cost per request on the live deployment, the same way Day 34 measured real latency, instead of guessing.

---

## What I Built

Added token usage + estimated cost tracking to `assistant.py`:

- A `PRICING` table (USD per 1M tokens, from Groq's published rates) and a `_usage_info(model, response)` helper that pulls `prompt_tokens`/`completion_tokens` off a Groq response and estimates cost.
- `answer_question()` now returns a `usage` field alongside its answer.
- `model_plan_action()` now returns `(action, usage)` instead of just `action`.
- `POST /ask` in `main.py` merges routing usage + answer usage into the response as a `usage` list and a `total_cost_usd` field, visible directly in the JSON — no server-log access needed, matching the client-side measurement approach from Day 34.
- `projects/day-36-cost-monitoring/measure_cost.py` — hits the live endpoint 5x for a RAG question and 5x for a tool question, reporting avg tokens/cost and a projected cost per 1000 requests.

## The Accidental Find

While testing this locally, `model_plan_action()` kept returning `None` for usage — even though the action it returned was correct. Testing the Groq client directly exposed why:

```
groq.NotFoundError: Error code: 404 - {'error': {'message': 'The model `llama-3.1-8b-instant` does not exist or you do not have access to it.', 'type': 'invalid_request_error', 'code': 'model_not_found'}}
```

Groq has decommissioned `llama-3.1-8b-instant` — the model `model_plan_action()` has used for routing since Day 25. Every single routing call has been silently failing and falling back to the rule-based `plan_action()`, caught by the exact `try/except` verified as a real safety net on Day 35. The fallback happening to return the same answer for simple cases (like "check git status") is what hid it — it took an ambiguous phrasing test to notice something was off, and cost instrumentation to prove it, since `usage` was always `None`.

## The Fix

Listed currently available Groq models directly (`groq_client.models.list()`) and switched the routing model to `openai/gpt-oss-20b` — the same model already confirmed working for `answer_question()`, rather than guessing at an unfamiliar replacement.

Confirmed both routing behaviors still work correctly with the new model:
- Rule-matchable phrasing ("check git status") → `check_git_status`, now with real usage data attached.
- Ambiguous phrasing the rule-based router can't handle ("what should I work on next", "tell me about vector embeddings") → correctly routed to `read_progress_files` and `answer_question` respectively.

## A Real Cost Tradeoff, Not A Free Fix

`openai/gpt-oss-20b` is a larger reasoning model than the old `llama-3.1-8b-instant`. Even for a one-word routing answer, it produced far more completion tokens (~35-80+ tokens of reasoning vs. what a small instruct model would need), so routing itself now costs more per call than it used to — not just "restored to the old cost," a real increase. Documented here rather than glossed over, since the whole point of this day was to measure cost honestly.

## A Second Bug, Found The Same Way

After fixing the model swap, `measure_cost.py` against the live endpoint showed **RAG questions only ever reported 1 model call** — the routing usage was still missing, just for a different reason. Reproducing the exact routing call directly showed why:

```python
resp = groq_client.chat.completions.create(model=ROUTING_MODEL, ...)
print(repr(resp.choices[0].message.content))  # ''
print(resp.usage)  # completion_tokens=50, reasoning_tokens=38
```

`gpt-oss-20b` is a reasoning model — it sometimes spends its whole completion budget on hidden reasoning tokens and returns an **empty** visible answer. The routing code did `action.splitlines()[0]`, which throws `IndexError` on an empty string, and that exception was swallowed by the same blanket `except Exception:` — losing the usage data yet again, and coincidentally still returning the right answer via `plan_action()`'s rule-based defaults for these specific test questions.

Fixed by guarding the empty-content case instead of relying on the exception path:
```python
lines = action.splitlines()
action = lines[0].strip() if lines else ""
```
Confirmed locally across 4 different queries (rule-matchable and ambiguous) that usage is now populated every time, not just when the model happens to return non-empty text.

## Real Numbers From The Live Deployment

Ran `measure_cost.py` (5 calls each) against `https://repo-assistant-api.onrender.com`, after both fixes were deployed:

| Question type | Avg tokens | Avg cost/request | Cost per 1000 requests |
|---|---|---|---|
| RAG ("what is temperature") | 875 | $0.00016 | $0.16 |
| Tool ("check git status") | 201 | $0.000034 | $0.03 |

RAG questions cost ~4.7x more than tool-routing questions — expected, since they pay for both the routing call and the full answer-generation call with retrieved context, while tool questions only pay for routing (the tool functions themselves are free local code).



- Confirmed the exception directly: `groq_client.chat.completions.create(model="llama-3.1-8b-instant", ...)` → `404 model_not_found`.
- Confirmed `groq_client.models.list()` no longer lists `llama-3.1-8b-instant` at all.
- Confirmed after the fix: `model_plan_action()` returns real, non-`None` usage dicts for both rule-matchable and ambiguous queries.
- Confirmed live: `/ask` on the deployed endpoint returns `usage` and `total_cost_usd` fields after redeploy.

## Key Learning

A `try/except` fallback that "works" (returns a valid answer, doesn't crash) can still be masking a real regression — silent degradation is still degradation. The bug wasn't found by reading the code again; it was found by trying to *measure* something (cost) that the broken path couldn't produce, because it never touched the real API at all.
