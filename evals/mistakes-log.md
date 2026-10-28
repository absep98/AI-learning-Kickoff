# Mistakes & Forgotten Things Log

One row per mistake or forgotten thing, logged as it happens (mid-session or in a test), grouped by concept. The revision block pulls from here first: ask about every `open` row before anything else. Mark a row `closed` only after two correct answers on separate days.

Fields: **Wrong** = what I did or believed. **Right** = the correct understanding. **Check** = a question to ask cold. **Status** = open / closed (date).

## Embeddings and RAG

| Date | Day | Wrong | Right | Check | Status |
| --- | --- | --- | --- | --- | --- |
| 2026-10-27 | 40 | Thought chunking had to be redone for 768 dims | Chunking is plain text splitting, independent of the embedding model; only the embedding step re-runs | Does switching embedding models change how notes are chunked? | open |
| 2026-10-27 | 40 | Thought 768 limits paragraph length | 768 is the output vector size; input limit is 2,048 tokens | `output_dimensionality=768` means what? | open |
| 2026-10-27 | 40 | "Same model" rule explained only as different vector lengths (384 vs 768) | Different dimension fails loudly; same dimension but different model fails silently with garbage distances | What breaks if the model changes but the dimension stays the same? | open |
| 2026-10-27 | 40 | Expected a stale collection to give wrong answers | It gives a Chroma dimension error | What error do you see when old 384-dim vectors meet a 768-dim query? | open |
| 2026-10-27 | 40 | Kept `DISTANCE_THRESHOLD = 0.75` after switching models; out-of-scope question got a fake-sourced answer | A threshold belongs to one model's distance scale; measure in-scope vs out-of-scope distances and pick inside the gap | Why did switching embedding models invalidate the old threshold, and how did you pick the new one? | open |
| 2026-10-27 | 40 | Believed vector normalization matters for cosine distance (my own hint, corrected) | Cosine distance ignores vector length | Does normalization change cosine distance? | open |
| 2026-10-27 | 40 | Recalled the old model's dimension as 368 | MiniLM is 384 | Dimensions of MiniLM vs the Gemini setup? | open |

## APIs, rate limits and retries

| Date | Day | Wrong | Right | Check | Status |
| --- | --- | --- | --- | --- | --- |
| 2026-10-27 | 40 | Used a Vertex AI quota table to judge the AI Studio free tier | Free tier is 100 embed texts/min per project/model; always check the quota source matches the product | What is the free-tier limit and why did it force offline ingest? | open |
| 2026-10-27 | 40 | Wrote a retry helper but never called it (and the wrapper had `attempt == MAX_RETRIES`, `err.Server` bugs) | Retry only 429/5xx, exponential backoff, and the helper must be on every call path, including the query embedding | Which errors should be retried, which not, and why? | open |
| 2026-10-27 | 40 | Batch loop overwrote `ids`/`metadatas` slices each pass | Build the full list across the loop; batch only the API call | (spot check in code review) | open |
| 2026-10-27 | 40 | Gemini SDK slips: `content=` vs `contents=`, `e.value` vs `e.values`, `embeddings.values` vs `embeddings[0].values`, wrong import forms, model name typo | Read the SDK reference before writing; test in a scratch file first | (spot check in code review) | open |

## Python and data handling

| Date | Day | Wrong | Right | Check | Status |
| --- | --- | --- | --- | --- | --- |
| 2026-10-27 | 40 | Mixed up `json.dump/dumps/load/loads` repeatedly (`json.dumps(entries, f)` writes nothing) | `dump`/`load` work with a file object; `dumps`/`loads` work with strings | Which json function writes to an open file, which returns a string? | open |
| 2026-10-27 | 40 | Loader read key `'embedding'` but the writer saved `'vector'` | Writer and reader of a shared file format must agree on key names; put them in one place or document them | What failed at runtime and how would you prevent it? | open |
| 2026-10-27 | 40 | Used `client` for both Gemini and Chroma; the later one silently overwrote the first | Use distinct names (`genai_client`, `chroma_client`) | What is name shadowing and where did it bite? | open |
| 2026-10-27 | 40 | Relative `OUTPUT_PATH = "./embeddings.json"` depends on the current directory | Build paths from `Path(__file__).parent` | Why is a path relative to `__file__` safer? | open |

## Process and workflow

| Date | Day | Wrong | Right | Check | Status |
| --- | --- | --- | --- | --- | --- |
| 2026-10-27 | 40 | Edited the live app file with half-written code before testing | Isolate in a scratch file, verify, then integrate | Why test in a scratch file first? | open |
| 2026-10-27 | 40 | Ran `assistant.py` before the loader was wired; the old rebuild burned the quota again | Check what runs at import/startup before running a file that can call a paid or limited API | What did running the file trigger, and what did it cost? | open |
| 2026-10-27 | 40 | Moved on after "it works" for in-scope questions only | Test the failure path too (out-of-scope question); that is where the fake-source bug was | Which test would have caught the threshold bug on day one? | open |

## Caching and Python references

| Date | Day | Wrong | Right | Check | Status |
| --- | --- | --- | --- | --- | --- |
| 2026-10-28 | 37 | Picked the right cause (caller mutated the cached dict) but could not explain why mutating a returned dict corrupts the cache | Dicts are passed by reference: the cache and the caller hold the same object, so `.pop()` in the caller changes the cached copy; return a copy (`dict(...)`) at the cache boundary | Why did every cache hit after the first crash, and what is the fix? | open |

## Evals

| Date | Day | Wrong | Right | Check | Status |
| --- | --- | --- | --- | --- | --- |
| 2026-10-28 | 41 | Edited the Day 16 eval instead of the Day 31 live eval; sleep placed outside the try block (SyntaxError) | Check which file hits the live endpoint; keep `time.sleep` in a `finally:` so it runs for errors too | Which eval talks to the live site, and why did it need a sleep? | open |
| 2026-10-28 | 41 | Predicted 4 requests would pass a limit of `len(recent) >= 5` | Requests 1-5 pass, the 6th is blocked | How many of 10 rapid requests pass a limit of 5 per 60 s? | open |
| 2026-10-28 | 41 | Proposed adding keywords to make a failing eval question pass without first confirming the answer was correct or naming the risk | Judge the answer first; loosening criteria can let wrong answers pass; the 0.6 ratio is meaningless for one keyword | App bug or eval bug, and what is the risk of the fix? | open |
| 2026-10-28 | 41 | Explained near-miss questions scoring close as "word overlap" | Embeddings capture meaning/topic, not keyword overlap; distance measures topical similarity, not "this chunk can answer the question", so a threshold cannot separate covered from adjacent topics | Why does "how does LoRA fine-tuning work" score close to notes that don't mention LoRA? | open |
| 2026-10-28 | 42 | `text.lower()` on its own line, result discarded; compared the function `normalize` to `""` instead of the normalized quote | Strings are immutable: methods return a new string, so assign or chain it; compare the variable, not the function name | Why does `text.lower()` alone not change `text`? | open |
