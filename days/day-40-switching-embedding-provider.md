# Day 40 - Switching the Embedding Provider (HF -> Gemini)

**Status: deployed.** RAG runs end-to-end locally and on the live Render site with Gemini embeddings and a re-tuned threshold (merged to `main` as `8b08071`). Live check: "what is temperature" answers with sources; "who won the 2018 World Cup?" returns "No relevant notes found".

## Why

Hugging Face's free Inference API ran out of credits (Day 38). Every RAG question calls `embed()` to vectorize the query, so retrieval has been broken since. Today's goal: replace it with the Gemini embeddings API.

## Concepts learned

- **Same model, same space.** Each embedding model learns its own private coordinate system. Chunks and queries must come from the same model. A different dimension (384 vs 768) fails loudly with a Chroma dimension error. A different model with the *same* dimension fails silently: no error, garbage distances. The silent case is the dangerous one.
- **Chunking is independent of the embedding model.** Switching models re-runs only the embedding step.
- **Input limit vs output size.** `gemini-embedding-001` accepts up to 2,048 tokens per text (input). The vector length (768) is the output size.
- **Default dimension is 3072;** 768 must be requested with `output_dimensionality`.
- **`task_type`** labels how a vector will be used: `RETRIEVAL_DOCUMENT` for stored chunks, `RETRIEVAL_QUERY` for the user's question.
- **Free-tier rate limit: 100 embed texts/min** (AI Studio, not the Vertex table I found first). Rebuilding ~800 chunks at startup would take 8+ minutes and burn query quota.
- **Build-time vs serve-time work.** Embed offline once (`ingest.py` -> `embeddings.json`, 799 chunks x 768, 8.7 MB), ship the vectors, and load them into Chroma at startup with no API calls. Missing file = loud warning + empty collection, not a slow rebuild.
- **Retry with exponential backoff** only for 429 and 5xx; clean up a partially built collection so "rebuild only if empty" does not skip an incomplete index.
- **A relevance threshold belongs to the embedding model.** `DISTANCE_THRESHOLD = 0.75` was tuned for MiniLM. With Gemini, an out-of-scope question ("who won the 2018 World Cup?") passed the gate and got an answer from the model's own knowledge with fake note sources.

## Threshold tuning (measured, not guessed)

`tune_threshold.py` printed the best distance for 5 in-scope and 5 out-of-scope questions:

| Group | Best-distance range |
|---|---|
| In-scope | 0.228 - 0.284 |
| Out-of-scope | 0.390 - 0.464 |

Set `DISTANCE_THRESHOLD = 0.35` (inside the gap, leaning toward in-scope). Result in the running app: the World Cup question now returns "No relevant notes found". Caveat: only 10 clear-cut questions; borderline questions need the Day 31 eval harness to tune further.

## What was built

- `assistant.py`: `embed(texts, task_type)` (Gemini), `_embed_with_retry`, `_load_vector_file`, `_build_collection_if_empty` loading `embeddings.json`, new collection name `ai_notes_gemini_768`, threshold 0.35.
- `ingest.py`: offline script; embeds in batches of 50 with a 35 s pause, writes a list of `{"text","source","vector"}`.
- `tune_threshold.py`: throwaway measurement script.
- `test_embed.py` (day-40 folder): isolated first test.

## Real mistakes made

1. Edited the live app file before testing in a scratch file.
2. Wrong import forms, missing comma, `content=` vs `contents=`, typo in model name, `e.value` vs `e.values`.
3. Name clash: `client` for both Gemini and Chroma.
4. Believed chunking depended on 768, and that 768 limited paragraph length.
5. Retry helper written but never called; wrapper bugs (`attempt == MAX_RETRIES`, `err.Server`).
6. `json.dump/dumps/load/loads` mix-ups, repeatedly.
7. Loader read key `'embedding'` but the file wrote `'vector'` (KeyError). Writer and reader of a shared file format must agree on key names.
8. Ran the app before wiring the loader and triggered the old rebuild, which hit the 100/min limit again.
9. Left 0.75 untouched after changing models and shipped a threshold tuned for a different embedding space.

## Test evidence

- `embed` returns 768-float vectors; ingest produced 799 x 768 with no 429 using the 35 s pause.
- App start: `[startup] Loaded 799 chunks from embeddings.json` with no API call.
- "what is temperature" and "why must index and query use the same embedding model?" answer correctly from the notes.
- "who won the 2018 World Cup?": fake-sourced answer at threshold 0.75; "No relevant notes found" at 0.35.

## Where we left off (next session)

Done after the first commit: query embedding now uses `_embed_with_retry`; HF import/client/docstring removed; warning text fixed; `google-genai` added to `pyproject.toml`/`uv.lock`/`requirements.txt`; `GOOGLE_API_KEY` set on Render; merged and pushed; live check passed.

Still open:
1. Re-run the Day 31 eval against the live app for a before/after number and to test the 0.35 threshold on borderline questions.
2. Only pass chunks that are individually under the threshold, not all 10 once the top one passes.
3. `ingest.py` must be re-run (and `embeddings.json` re-committed) when notes change; add a staleness check.
4. Retry covers short blips only (waits of 1/2/4 s); a free-tier 429 can ask for 19-48 s.
