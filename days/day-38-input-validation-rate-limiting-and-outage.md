# Day 38 — Input Validation, Rate Limiting, And A Real Production Outage

**Goal:** Close out Month 4's remaining checklist items — input length limit and rate limiting — both still unchecked in `roadmap.md`.

---

## Part 1: Input Length Limit

Added a `max_length` constraint directly on the Pydantic field:
```python
text: str = Field(..., max_length=422)
```
Confirmed: an oversized request is rejected automatically with a `422`, before `/ask`'s function body ever runs — no custom validation code needed, Pydantic handles it at the boundary.

## Part 2: Per-IP Rate Limiting

Built a 5-requests-per-60-seconds limiter using the same dict+timestamp pattern as Day 37's TTL cache — same building block, different purpose (client → request history instead of question → cached answer).

Real mistakes made building it (documented honestly, not hidden):
1. Called a dict like a function (`_request_log(ip, [])` instead of `.get(ip, [])`).
2. Capitalized `time.Time()` instead of `time.time()`.
3. Referenced an undefined `N` variable.
4. **Logic inversion** — initially recorded a request only inside the "reject" branch, meaning the counter could never actually grow on allowed requests, so the limit could never trigger at all.
5. **Found in production, not locally:** the rate limiter worked perfectly on `localhost` but never triggered once deployed live. Root cause: `request.client.host` reports Render's reverse-proxy address, not the real caller's IP — every request looked identical (or inconsistent) to the limiter, so per-client counts never accumulated correctly. Fixed by reading the `X-Forwarded-For` header (which proxies set to the real client IP) first, falling back to `request.client.host` only when absent (e.g. local dev, no proxy in front).
6. Building that fix took two more iterations: first attempt had the `if`/`else` branches swapped, second attempt indexed the header string directly (`forwarded[0]`, grabbing a single character) instead of splitting on comma first.

Confirmed live: 5 requests succeed, 6th+ within the same minute get a real `429 Too Many Requests`.

## An Unrelated Real Production Outage (found mid-session)

While testing the rate-limiter fix live, Render sent a genuine crash alert: **"Exited with status 1."** The live site was down — confirmed directly (`/` timing out, `/ask` returning 503).

**Root cause (from the actual traceback):** Hugging Face's Inference API returned `402 Payment Required` — "You have no remaining credits." This crashed `_build_collection_if_empty()` during module import, which crashed the **entire app at startup**, not just one request.

**Why this could even happen:** `chroma_db/` is gitignored and Render's filesystem is ephemeral — so *every single deploy* rebuilds the full 697-chunk collection from scratch via the HF embedding API, a fact that's been true (and silently fine) since Day 29. The moment HF's free credits ran out, every future deploy was guaranteed to crash at startup, with no degraded mode — because `_build_collection_if_empty()` was called with no error handling at module level.

**The fix:** wrapped the startup rebuild call in a `try/except`. If it fails for any reason (API outage, exhausted credits, network error), the app now logs a warning and boots anyway, with an empty collection, instead of refusing to start entirely. `check_git_status` and `read_progress_files` keep working regardless of RAG's embedding dependency being available; `answer_question` degrades (no retrieved context) instead of taking the whole service down.

Confirmed live: redeployed, service came back online, rate limiter re-verified working correctly afterward.

## Key Learning

Two separate lessons, from two separate incidents, in the same session:
1. **A feature that works perfectly in dev can be silently broken in production** for an environment-specific reason (a reverse proxy) that local testing can never surface — the only way to know was testing against the real deployed URL, not just `localhost`.
2. **An unrelated dependency with no error handling at startup is a single point of total failure.** The HF outage wasn't caused by anything we touched today, but the blast radius was "the entire app can't boot" instead of "RAG answers degrade gracefully" — purely because nothing caught the exception. Defensive error handling around external API calls at startup isn't optional polish; it's the difference between a full outage and a graceful degradation.
