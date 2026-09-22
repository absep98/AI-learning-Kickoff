# Day 28 — Removing The Ollama Deployment Blocker

**Goal:** Solve the last real blocker before `assistant.py` can be deployed to a cloud server — the embedding call depended on local Ollama (`http://localhost:11434`), which only exists on my own machine.

---

## Why This Mattered

Groq (the LLM call) already worked fine from anywhere, since it's a cloud API — you send a request to `groq.com`, doesn't matter what machine you're on. But Ollama isn't a cloud API; it's a program installed only on my laptop. A deployed server is a *different machine*, so it can never reach `localhost:11434` on my laptop. Every "connection refused" error hit earlier in this project was this exact issue.

## What Was Built

- Installed `sentence-transformers` (`uv add sentence-transformers`).
- Loaded the embedding model directly in Python instead of calling out to Ollama's HTTP API: `embed_model = SentenceTransformer("all-MiniLM-L6-v2")` — loaded once at module level (same pattern as `groq_client` and `collection`), not reloaded per request.
- Replaced the Ollama HTTP call inside `retrieve_chunks()`:
  ```python
  # before
  query_resp = requests.post(OLLAMA_URL_EMBEDDING, json={"model": EMBED_MODEL, "input": query})
  query_vector = query_resp.json()["embeddings"][0]

  # after
  query_vector = embed_model.encode(query).tolist()
  ```
- Removed now-unused `OLLAMA_URL_EMBEDDING`, `EMBED_MODEL` constants and the `requests` import.

## Test Evidence

- `retrieve_chunks("what is temperature")` distance: **0.4552** via `sentence-transformers`, vs. **0.4551** via Ollama for the same query — confirms mixing embedding sources (documents embedded via Ollama at index time, queries now embedded via `sentence-transformers`) doesn't meaningfully hurt retrieval, since it's genuinely the same underlying model (`all-MiniLM-L6-v2`).
- Confirmed `384`-dimension output matches Ollama's `all-minilm` output size before wiring it in.

## Bugs Fixed Along The Way

- Import typo (`sentence_tranformers` instead of `sentence_transformers`) — caught twice before it was correct.
- `client` was referenced by `collection = client.get_collection(...)` before `client` itself was defined further down the file — reordered.
- A stray leftover `ok` token inside `collection.query(ok ...)` — invalid as a function argument, removed.
- Embedding model was initially loaded *inside* `retrieve_chunks()`, meaning it would reload from disk on every single call — moved to module level.

## File Updated

- `projects/day-27/awesome-project/assistant.py`

## Key Learning

"Runs on my machine" and "runs on a server" are not the same thing whenever code depends on something reachable only via `localhost`. The fix isn't just "make it configurable" (that only helps for things like file paths) — for a local-only *service* like Ollama, the real fix is removing the network dependency entirely by running the same computation in-process.

## Next Step

Actually deploy the FastAPI app (Render/Railway/etc.) and get a live URL — the last step toward a portfolio-worthy, demoable feature.
