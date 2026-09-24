# Day 34 — Measuring And Fixing Latency On The Deployed Assistant

**Goal:** Measure real latency of the live `/ask` endpoint, find the actual bottleneck (not an assumed one), and fix it for free.

---

## Measurement Setup

Wrote `projects/day-31-deployed-evals/measure_latency.py` — sends the same question 5 times to `https://repo-assistant-api.onrender.com/ask`, timing each call with `time.time()`. Tested two question types to isolate where cost comes from:
- A RAG question ("what is temperature") — pays for embedding (Hugging Face API) + ChromaDB lookup + Groq generation with retrieved context.
- A tool-routing question ("check git status") — still pays for the Groq planner call (every `/ask` request routes through `model_plan_action` first), but skips embedding and RAG generation entirely.

## Finding #1 (the big one): Render free-tier cold start

First run:
```
--- RAG question ---
call 1: 43.58s   <- cold start
call 2: 1.30s
call 3: 1.36s
call 4: 0.94s
call 5: 0.82s
```
Render's free tier spins the service down after inactivity. The very first request after a period of no traffic pays a **43+ second** penalty just to wake the server up — dwarfing every other latency concern. For a live demo link meant to represent real work, this is a much bigger problem than RAG-vs-tool speed differences.

## Fix #1: Free keep-alive ping (no cost)

Set up a free cron job on [cron-job.org](https://cron-job.org) hitting `https://repo-assistant-api.onrender.com/` (the fast root health-check route, not `/ask`) every **10 minutes** — safely inside Render's ~15-minute sleep window. This keeps the instance permanently warm without paying for an always-on paid tier.

**Confirmed fixed** — after the cron job ran for ~30 minutes, re-measured:
```
--- RAG question ---
call 1: 2.40s
call 2: 1.20s
call 3: 0.89s
call 4: 1.60s
call 5: 1.24s
```
No outlier. Call 1 is now consistent with the rest.

## Fix #2: UX honesty in the meantime

Before the keep-alive fix was confirmed working, added a note to the `/chat` page and the "Thinking..." loading state warning that the first request after inactivity may take up to a minute — so a visitor hitting a rare cold start isn't left confused, wondering if the page is broken.

## Finding #2 (smaller): RAG path is ~3x slower than the tool path in steady state

- RAG average: **~1.47s**
- Tool average: **~0.44s**

Expected — every request pays for the Groq planner call first (routing decision), and RAG additionally pays for a Hugging Face embedding round-trip plus a longer Groq generation call with retrieved context. Not fixed in this session — 1.5s is a reasonable response time for a RAG feature and not worth added complexity (e.g. caching) to shave further right now.

## Key Learning

Measure before optimizing — the actual bottleneck (a 43-second cold start affecting every first-time visitor) was completely different from, and far more impactful than, the assumed bottleneck (RAG vs. tool routing speed). Caching the RAG path — the fix planned before measuring — would have done nothing for the actual problem. Real numbers changed the plan entirely, which is the point of measuring first.

## Files Updated

- `projects/day-31-deployed-evals/measure_latency.py` (new)
- `projects/day-27/awesome-project/main.py` (cold-start UX warning)
- External: a free cron-job.org keep-alive ping (not part of the repo, configured on cron-job.org's dashboard)
