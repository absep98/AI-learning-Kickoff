# Day 37 — TTL-Based Answer Caching (And A Cache-Poisoning Bug)

**Goal:** Direct follow-on from Day 36's cost data — RAG questions cost ~4-5x more than tool questions because every question pays for a fresh Groq call, even repeats of the exact same question. Add caching so repeat questions are free and instant.

---

## What Was Built

- `_answer_cache` — an in-memory dict in `assistant.py`, keyed by the normalized question text, storing `(result, timestamp)` tuples.
- `answer_question()` checks the cache before doing any retrieval or Groq calls; a fresh miss computes normally and stores the result; a hit within `CACHE_TTL_SECONDS` (10 minutes) returns instantly without touching the network at all.
- TTL exists for correctness, not memory — the real risk isn't cache size (a personal demo has maybe dozens of distinct questions, trivial memory), it's staleness: `days/*.md` notes get added regularly, so a cached answer needs to expire and get recomputed periodically rather than being trusted forever.

## Real Mistakes Made While Building This (documented, not hidden)

Building the cache surfaced a chain of real bugs, each one a genuine lesson:

1. **`NameError`** — first attempt referenced a `key` variable that was never defined.
2. **Cache check placed after the expensive calls** — checking the cache *after* `retrieve_chunks()` and the Groq call had already run defeats the entire point of caching.
3. **Nothing ever wrote to the cache** — even after fixing 1 and 2, no line ever did `_answer_cache[key] = ...`, so the cache stayed empty forever.
4. **Ordering bug causing a `KeyError`** — the freshness check (`_answer_cache[query]`) ran *before* confirming the key existed, so any brand-new question crashed instantly.
5. **A real cache-poisoning bug** (the most subtle one): `main.py`'s `/ask` route mutates the dict it gets back (`result.pop("usage")`, then reassigns `result["usage"]`). Since Python dicts are passed by reference, and the dict returned by `answer_question()` was the *same object* stored in `_answer_cache`, that mutation corrupted the cached entry itself. First call always worked; every subsequent cache hit crashed with `TypeError: list indices must be integers or slices, not str`, because the cached `"usage"` field had been silently rewritten from a dict into a list, then a list-of-lists, on each mutation.

## The Fix

Root-caused to the cache boundary, not the caller: `answer_question()` was handing out direct references to objects living inside its own cache. Fixed by copying at both handoff points:
- **On a cache hit**, return `dict(cached_result)` — a fresh copy, not the cached object itself.
- **On a cache miss**, store a *separate* copy in `_answer_cache` (`dict(result)`) rather than the same object being returned to the caller.

This protects every current and future caller of `answer_question()` from this class of bug, not just `main.py`'s specific mutation pattern.

## Test Evidence

- Reproduced the crash locally by simulating the exact `main.py` logic against a repeated question — confirmed it broke on the 2nd call even with only the cache-hit-side copy fix (the cache-miss path was still handing out the shared object). Fixing both handoff points resolved it — 4 consecutive identical calls succeeded.
- Confirmed live: deployed the fix, ran 4 consecutive identical questions against `https://repo-assistant-api.onrender.com/ask` — all succeeded, all returned identical `total_cost_usd`, no crashes.
- Confirmed staleness handling separately (with `CACHE_TTL_SECONDS` temporarily set to 5 for testing): waited past the TTL and verified the entry was recomputed (a fresh timestamp), not incorrectly served stale.

## Key Learning

A cache that hands out direct references to its own internal storage is fragile — any caller that mutates what it gets back corrupts the cache for every future request, and the failure only shows up on the *second* access, not the first, making it easy to miss in casual testing. The fix isn't "don't mutate things" (callers will always have their own reasons to reshape data) — it's "a cache should never expose its internal objects directly; always hand out a copy at the boundary."
