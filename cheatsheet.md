# AI Concepts Cheat Sheet

Quick-reference glossary of every concept learned so far. Use this for fast revision — each entry is 1-2 lines with a link to the full explanation.

Last updated: Day 42 (Days 31-39 not yet summarised here, see their day notes)

---

## Core Concepts

| Concept | One-Line Definition | Deep Dive |
| --- | --- | --- |
| **LLM** | A neural network trained on text to predict the next token — repeat billions of times and it simulates reasoning. | [Day 01](days/day-01-llm-basics.md) |
| **Token** | The basic unit an LLM processes — usually a word-piece, not a full word. `"unbelievable"` → `["un", "believ", "able"]`. | [Day 01](days/day-01-llm-basics.md) |
| **Tokenization** | Breaking text into tokens so the model can process it as numbers. Code uses more tokens than English. | [Day 01](days/day-01-llm-basics.md), [Day 03](days/day-03-corrections-and-gaps.md) |
| **Context window** | The model's whiteboard — everything (prompt + history + reply) must fit. Old content drops when full. | [Day 02](days/day-02-temperature-context-embeddings.md) |
| **Temperature** | Controls how the model samples from its probability distribution. Low = safe/deterministic. High = creative/random. Does NOT add knowledge. | [Day 02](days/day-02-temperature-context-embeddings.md) |
| **Embeddings** | Vectors (lists of floats) that encode meaning. Similar meaning → similar vectors → close in vector space. | [Day 02](days/day-02-temperature-context-embeddings.md), [Day 03](days/day-03-corrections-and-gaps.md) |
| **Attention mechanism** | Lets the model decide which earlier tokens matter most right now. The "T" in GPT = Transformer. | [Day 01](days/day-01-llm-basics.md) |
| **Transformer** | The architecture that powers modern LLMs. Uses attention to process relationships between all tokens simultaneously. | [Day 01](days/day-01-llm-basics.md) |
| **Parameters** | The billions of trained weights inside a model. More = smarter but slower and heavier. 3.8B vs 70B vs 100B+. | [Day 05](days/day-05-inference-local-models-api-lifecycle.md) |
| **Hallucination** | When an LLM confidently generates incorrect or made-up information. Not "forgetting" — it is generating plausible patterns that happen to be wrong. | [Day 01](days/day-01-llm-basics.md), [Day 03](days/day-03-corrections-and-gaps.md) |

---

## The Internal Pipeline

```
Text → Tokenization → Embedding Layer (representation)
  → Transformer + Attention (processing)
  → Probability Distribution (prediction)
  → Temperature Sampling (selection)
  → Next Token
  → Repeat
```

| Stage | What it does | Key point |
| --- | --- | --- |
| **Tokenization** | Breaks text into token IDs | Input preparation, not intelligence |
| **Embedding layer** | Converts token IDs to meaning vectors | Representation, NOT prediction. A lookup table. |
| **Transformer + attention** | Processes relationships between all tokens | Where the actual "intelligence" lives |
| **Output layer** | Produces probability distribution over all possible next tokens | Prediction step |
| **Sampling** | Picks one token based on temperature | Selection step |

Full explanation: [Day 03](days/day-03-corrections-and-gaps.md)

---

## RAG (Retrieval-Augmented Generation)

**What it is:** Retrieve relevant document chunks via embedding similarity, then send only those chunks to the LLM — no retraining needed.

**What it is NOT:** Privacy/local hosting (that was a wrong assumption — corrected in Day 03).

```
Setup:  documents → chunk → embed → vector DB
Query:  question → embed → similarity search → retrieve chunks → LLM → answer
```

| RAG vs | Cost | When to use |
| --- | --- | --- |
| RAG | Low | Answer from specific documents |
| Fine-tuning | Medium | Learn a specific style/behavior |
| Retraining | Extreme | Fundamentally different model (rarely needed) |

Full explanation: [Day 03](days/day-03-corrections-and-gaps.md)

---

## Search Engine vs LLM

| | Search Engine | LLM |
| --- | --- | --- |
| Core action | **Retrieves** existing pages | **Generates** new text |
| Can hallucinate? | No | Yes |
| Output | Links to sources | Synthesised answer |

Modern AI = search retrieves facts + LLM synthesises answer. Full explanation: [Day 03](days/day-03-corrections-and-gaps.md)

---

## API & Inference

| Concept | One-Line Definition | Deep Dive |
| --- | --- | --- |
| **Inference** | Using a trained model to generate output. Every API call = inference. The model is not learning from you. | [Day 05](days/day-05-inference-local-models-api-lifecycle.md) |
| **Statelessness** | LLMs have no memory between requests. "Memory" = the app re-sending full chat history every time. | [Day 05](days/day-05-inference-local-models-api-lifecycle.md), [Day 06](days/day-06-hands-on-ollama-experiments.md) |
| **System prompt** | An instruction that shapes HOW the model behaves (persona, format, constraints) before the user says anything. | [Day 05](days/day-05-inference-local-models-api-lifecycle.md) |
| **max_tokens** | Limits output length. Set too low = response cut mid-sentence. Controls cost and speed. | [Day 05](days/day-05-inference-local-models-api-lifecycle.md) |
| **Streaming** | Token-by-token delivery instead of waiting for full response. Same total time, better UX. | [Day 05](days/day-05-inference-local-models-api-lifecycle.md) |
| **Prompt engineering** | Persona, format, and instruction control — the biggest lever for output quality. | [Day 05](days/day-05-inference-local-models-api-lifecycle.md) |

---

## Chat History Format (Standard Across APIs)

```json
[
  { "role": "system",    "content": "You are a helpful assistant." },
  { "role": "user",      "content": "What is Go?" },
  { "role": "assistant", "content": "Go is a statically typed..." },
  { "role": "user",      "content": "How do goroutines work?" }
]
```

Three roles: **system** (behavior), **user** (you), **assistant** (model's replies). Full history re-sent every request.

---

## Local vs Cloud Inference

| | Local (Ollama) | Cloud (OpenAI, Anthropic, Google) |
| --- | --- | --- |
| Cost | Free | Per-token |
| Speed | Slow (CPU) | Fast (GPU clusters) |
| Privacy | Full control | Data leaves your machine |
| Models | Small (3-8B) | Large (100B+) |
| Best for | Learning, prototyping | Production, complex tasks |

Ollama API: `POST http://localhost:11434/api/generate` — same HTTP pattern as cloud APIs.

Full explanation: [Day 05](days/day-05-inference-local-models-api-lifecycle.md), [Day 06](days/day-06-hands-on-ollama-experiments.md)

---

## Embeddings — Two Different Uses

| Use | Where | What it does |
| --- | --- | --- |
| Inside LLM | Internal embedding layer | Converts input tokens to vectors before transformer processes them |
| For search/RAG | Separate embedding model API | Converts sentences to vectors for similarity comparison |

Both are "vectors representing meaning" but different stages and purposes. Full explanation: [Day 03](days/day-03-corrections-and-gaps.md)

---

## Cosine Similarity

Measures the angle between two vectors. Similar direction = similar meaning, regardless of vector length. This is how vector databases find relevant document chunks.

Full explanation: [Day 03](days/day-03-corrections-and-gaps.md)

---

## Compound AI System Formula

```
Modern AI product = Model + Retrieval + Tools + Memory + UI
```

Raw LLM alone is NOT the product. The orchestration is. Full explanation: [Day 06](days/day-06-hands-on-ollama-experiments.md)

---

## Practical Quick-Reference

### Temperature Guide

| Use Case | Temperature |
| --- | --- |
| Code, SQL, JSON | 0.1–0.3 |
| Customer support | 0.3–0.5 |
| General chatbot | 0.7 |
| Creative writing | 0.9–1.2 |

### Token Approximation

- 1 token ≈ 0.75 English words
- Code uses ~2-3x more tokens than English text of same visible length
- Cost = (input_tokens × input_price) + (output_tokens × output_price)
- Output tokens cost 2-4x more than input tokens

### Context Window Sizes

| Size | Handles |
| --- | --- |
| 8K | Short conversations |
| 32K | Moderate documents |
| 128K | Large codebases, books |
| 1M+ | Entire libraries |

### Attention Cost

n tokens → n² attention computations. 10x more tokens = 100x more compute. This is why RAG beats brute-force context stuffing.

---

## What NOT To Learn Yet

| Topic | Why not yet |
| --- | --- |
| LangChain / LlamaIndex | Hides fundamentals |
| AI Agents | Need tools + prompting + memory first |
| Fine-tuning | Expensive, rarely needed for app builders |
| Multi-agent systems | Need single-agent basics first |
| CUDA / GPU programming | Infrastructure, not application |

---

## Concepts I Got Wrong Initially (Important for Revision)

| Wrong belief | Correction | See |
| --- | --- | --- |
| Embeddings predict next tokens | Embeddings are representation only. Transformer + attention do prediction. | [Day 03](days/day-03-corrections-and-gaps.md) |
| RAG is about privacy/local hosting | RAG is about retrieval efficiency — avoiding expensive retraining | [Day 03](days/day-03-corrections-and-gaps.md) |
| LLMs are like better search engines | Search retrieves existing info. LLMs generate new text. Different. | [Day 03](days/day-03-corrections-and-gaps.md) |
| LLMs are smart because of "lots of data" | Language contains reasoning patterns. Prediction at scale learns structure. Emergence. | [Day 03](days/day-03-corrections-and-gaps.md) |
| AI "remembers" conversations | Memory is fake — the app re-sends full history every request | [Day 05](days/day-05-inference-local-models-api-lifecycle.md), [Day 06](days/day-06-hands-on-ollama-experiments.md) |
| 1 token ≈ 0.75 words | Backwards — 1 word ≈ 1.33 tokens (Day 07 revision test caught this) | [Day 07](days/day-07-pipeline-hands-on.md) |

---

## Days 07–30 — Hands-On Builds (RAG → Tool-Calling Agent → Deployed Product)

### Tokenization & Embeddings, Proven With Real Code (Day 07)

- Ran `tiktoken` for real: English ≈ 1.0 tokens/word, code ≈ 2.2x, Hindi (non-English) ≈ 3.4x — tokenizer is English-optimized.
- Embedding model (`all-minilm`) vs chat model (`phi3:mini`) are trained for different jobs — forcing a chat model to embed gives garbage similarity scores (0.16 for "cat"/"kitten"). Only use models trained specifically for embeddings.
- Proved cosine similarity gradient makes sense: car/automobile 0.86 > cat/kitten 0.79 > cat/dog 0.66 > cat/car 0.46 > cat/python 0.24.
- Steps 3-5 of the pipeline (transformer/attention, probabilities, sampling) are a black box — only observable indirectly (temperature changes variety, longer input = slower, same prompt ≠ same output).

### Terminal Chatbot — The 4-Step Loop (Day 08)

```
1. Take user input
2. Append user message to history
3. Send FULL history to the API
4. Append assistant response to history
```
- This loop, repeated, is the core of every chat product (ChatGPT included) — the "memory" is just a Python list, not the model.
- Universal chat message format: `{"role": "system|user|assistant", "content": "..."}` — same across Ollama, OpenAI, Groq, Anthropic.
- Streaming = Ollama sends one JSON line per token; parse + `print(..., flush=True)` for the typing effect.

### Semantic Search + Pooling (Day 09)

- Semantic search: embed docs once at startup, embed query per request, rank all docs by cosine similarity — zero keyword overlap needed ("parallel tasks" → finds "goroutines").
- **Pooling** is the missing step that turns per-token vectors into one sentence vector: mean pooling (average all token vectors) or CLS token (one token absorbs whole-sentence meaning via attention). Embedding models pool; generation models predict-next-token instead.
- Rule: query and documents MUST use the same embedding model or the vector spaces don't match.

### RAG v1 — Retrieval + Generation Combined (Day 10)

- RAG = semantic search (Day 09) + chatbot (Day 08). Retrieved chunks get injected into the user message: `f"Context:\n{chunks}\n\nQuestion: {query}"`.
- History is reset fresh every query in RAG (unlike the accumulating chatbot) because context changes per question.
- Two-model architecture: embedding model retrieves, generation model synthesizes. Neither replaces the other.
- RAG beats fine-tuning for most product use cases: low cost, instantly updatable, uses your exact docs.

### Chunking — RAG Over Real Notes (Day 11)

- Chunking = splitting large docs into paragraph-sized pieces before embedding (needed because of context-window truncation, signal dilution, and retrieval precision).
- Filtering out short chunks (<80 chars) removes markdown noise (headings, table dividers) cheaply.
- **Golden rule:** when a RAG answer is wrong, debug retrieval first — print the retrieved chunks, don't assume the model is "dumb."
- Chunking tradeoff: too large → truncation + diluted signal; too small → lost context + more noise.

### Production RAG Hardening (Day 12)

- Persistent embeddings cache (`embeddings.json`): embed once, load instantly forever; only rebuild when the corpus/chunking/model changes.
- Source tracking: store `{chunk: {source, vector}}` so every retrieved chunk shows which file it came from — turns retrieval from a black box into something debuggable.
- Source deduplication: cap chunks-per-file (e.g. max 2) so one file can't dominate all retrieval slots.
- Score threshold: refuse to answer if the best match is below ~0.4 similarity — prevents hallucinating from irrelevant context.
- **Retrieval vs generation debugging split:** wrong chunks retrieved = retrieval bug (fix chunking/threshold/dedup); right chunks but wrong answer = generation/model limitation (upgrade model).

### Structured JSON Output (Day 13)

- Two levers to get JSON instead of prose: (1) system prompt demands exact JSON schema, (2) `stream: False` (can't parse JSON mid-stream).
- Small models (phi3:mini) often wrap JSON in ```` ```json ... ``` ```` fences even when told not to — always strip fences + extract `{...}` defensively before `json.loads()`.
- Don't trust a model's self-reported `"confidence"` — compute it from retrieval scores instead (`score > 0.7 → high`).
- Structured output is what lets AI plug into real systems: filter by confidence, log to a DB, route to fallback, feed downstream APIs.

### ChromaDB — Real Vector Database (Day 14)

- Replaces the manual JSON-file + cosine-loop with `PersistentClient` (folder on disk, like SQLite) + a `collection` (like a DB table).
- **Must set `metadata={"hnsw:space": "cosine"}`** — ChromaDB defaults to L2/Euclidean distance, which breaks similarity thresholds tuned for cosine.
- `collection.query(query_embeddings=[...], n_results=5)` replaces ~20 lines of manual sort/dedup/loop.
- HNSW = approximate-nearest-neighbor index, ~O(log N) search vs a JSON loop's O(N) — critical once corpora reach millions of chunks.
- ChromaDB returns **distances** (lower = more similar) — opposite sign convention from manual cosine **scores** (higher = more similar). Threshold checks flip accordingly.

### Cloud API Swap — Groq + Llama (Day 15)

- Swapping local `phi3:mini` for Groq's `llama-3.1-8b-instant` changed ~8 lines of code — everything else (ChromaDB, chunking, embeddings) was untouched, and answer quality jumped immediately.
- **Proved retrieval and generation are independent problems** — same retrieved chunks, different generation model, correct vs wrong answer.
- Groq uses the OpenAI-compatible format (`messages=[{role,content}]`, `response.choices[0].message.content`) — same pattern reusable across most cloud LLM providers.
- API key hygiene: `.env` uses `KEY=value` (no `$env:`, no quotes), always `.gitignore`'d, rotate immediately if a key is ever exposed in chat/logs.
- Groq (fast inference provider) ≠ xAI/Grok (Elon Musk's company) — easy to confuse, different products, different key formats.

### RAG Evals — Systematic Testing (Day 16)

- Built `eval_questions.json` (20 Q&A pairs with `expected_answer` + `expected_sources`) and `run_eval.py` to check both answer-content and source-retrieval automatically.
- Answer matching: normalize dashes/case, accept substring OR ≥60% word overlap — too strict (100% match) breaks on phrasing, too loose (20%) accepts wrong answers.
- Baseline 5% → 60% → final 80% (16/20), reached via 3 loops: retrieval debugging, refining eval expectations, repeated re-runs with measurable tracking.
- Low pass rate is *useful* signal, not discouragement — it exposed a real config bug (a whole day's notes was excluded via `SKIP_FILES`).
- Refactored the RAG script into `query_rag()` (callable/importable) + `interactive_loop()` — a `while True` at module level blocks any automated import/testing.

### Git AI Summary CLI (Day 17)

- Built a CLI (`git_ai_summary.py`) that captures `git diff` via `subprocess`, sends it to Groq with a strict JSON schema prompt, and prints "What Changed / Risky Changes / Suggested Commit Message."
- Supports 3 modes: `unstaged`, `staged`, `both` — diff capture via `subprocess.run(capture_output=True)`, never shell-piped directly.
- Truncates diffs to 12K chars to avoid token overflow; still needs markdown-fence stripping + fallback parsing even at `temperature=0`.

### Workflow Loop Foundations — Memory Scopes & Tool-Calling Rules (Day 18)

- Memory scope rules: **persistent** = stable user prefs across sessions; **session** = current chat's in-progress state; **repo** = project conventions/architecture; **never store** secrets/API keys/PII.
- Controlled tool-calling loop pattern: max step limit (e.g. 8) to prevent runaway execution; retry only transient failures (max 3 attempts), never retry deterministic errors; stop on success, user-quit, missing input, or repeated failure.
- Log every step with: intent, tool/action taken, context used, result, next decision — this is the backbone of any inspectable agent.
- Built `mock_loop.py` — first runnable prototype with `StepLog` dataclass, a rule-based `plan_action`, retry wrapper, one-shot/multi-turn toggle.

### Real Planner + Real Tool Executor (Day 19)

- Split the loop into **planner** (LLM suggests an action) → **guardrails** (constrain to an allowed-action set) → **executor** (runs only approved actions) → **logging/stop policy**. This planner/executor split is the core pattern of every safe tool-using agent.
- Always keep a deterministic fallback planner — never trust the model's raw output unchecked.

### Decision Metadata & Extended Tools (Day 20)

- Added `check_git_status` as a third real tool action.
- Added `planner_source` (model vs fallback) and `retry_attempts` to every `StepLog` — the difference between a debug print and a real production agent trace: you can see not just *what* happened but *how it was decided* and *how reliably*.

### Persisting Run Logs (Day 21)

- Console output disappears when the terminal closes. `persist_logs()` writes each run's full step trace to a timestamped JSON file in `run_logs/` (gitignored — these are local artifacts, not tracked history).
- Turns every run into a reviewable, diffable artifact instead of a one-time live demo.

### Conversation History In The Planner (Day 22)

- Gave the model planner memory of prior steps in the same run by replaying `{intent, action}` pairs as alternating real `user`/`assistant` chat turns — not a text blob appended to one prompt.
- Same statelessness lesson as Day 6/8 (the model has no memory; you replay history), just applied to an agent loop instead of a chatbot.
- This closed out Month 2 Option C: "build a controlled multi-step assistant workflow" (Days 18-22 combined).

### Hardening The Workflow Loop (Day 23)

- Fixed stale `pending_items` metadata, added `build_final_response()` for a natural-language summary instead of a raw action list.
- Added `failed_actions` surfacing — tools that fail even after retries are now reported, not silently swallowed.
- Added an early-exit stop condition: 2 consecutive `ask_clarification` results stop the loop instead of burning all 8 steps.
- **Lesson:** a loop isn't done when it "works" — it's done when it handles its own failure modes without a human watching every run.

### Repo Assistant — RAG + Tool Routing Shipped (Day 24)

- Combined Day 14's RAG retrieval with Days 18-23's tool-calling loop into one assistant (`repo_assistant.py`): `retrieve_chunks()`, `answer_question()`, `check_git_status()`, routed by a rule-based `plan_action()`.
- **Lesson:** retrieval and generation must be separate functions, not one inline block — otherwise you can't reuse just the retrieval half later (for routing, evals, or deployment).

### Model-Based Planner For Repo Assistant (Day 25)

- Replaced keyword-only routing with `model_plan_action()` (Groq, `temperature=0`), validated against an `ALLOWED_ACTIONS` set, with automatic fallback to the rule-based router on invalid/failed output.
- Proved it routes correctly on rephrased/non-keyword input ("tell me about my commits" → `check_git_status`).
- **Lesson:** any model-based router needs the same discipline as any AI-in-the-loop system — validate output against a known-safe set, always keep a non-AI fallback.

### Third Tool — read_progress_files (Day 26)

- Added a tool that reads `progress.md` directly for "what day am I on" style questions, instead of letting those fall through to RAG (which was confidently hallucinating answers from unrelated retrieved chunks with real-looking citations attached).
- **Lesson:** a RAG system with no way to say "not in my documents" will confidently retrieve *something* wrong. A dedicated tool for a known question type beats trying to make retrieval smarter.

### FastAPI Wrapper — CLI → Web API (Day 27)

- Ported all of `repo_assistant.py` into a `uv`-managed FastAPI project; `POST /ask {"text": "..."}` routes through `model_plan_action` to the right function, verified via Swagger UI (`/docs`).
- Made `REPO_ROOT` and the ChromaDB path environment-variable-configurable — first step toward deployment, since a cloud server has no `C:\learning\aithings`.
- **Lesson:** a CLI prototype and a deployable API are architecturally different even with identical logic — the API needs its own project boundary, env-based config, and a request/response contract (Pydantic) instead of `input()`/`print()`.
- Remaining blocker identified: retrieval's embedding call still depended on local Ollama (`localhost:11434`), which won't exist on a deployed server.

### Removing The Ollama Deployment Blocker (Day 28)

- Ollama is a program on your laptop, not a cloud API — a deployed server is a different machine and can never reach your `localhost`. Groq worked everywhere already because it's a real cloud API.
- Fix: load `sentence-transformers` (`all-MiniLM-L6-v2`) directly in-process instead of calling Ollama's HTTP API — same model, same 384-dim vectors, no network dependency.
- **Lesson:** for a local-only *service* dependency (not just a file path), the real fix is removing the network dependency entirely, not just making the URL configurable.

### Deploying To Render — Real Production Blockers (Day 29)

- 4 real blockers hit in order: (1) `requirements.txt` never committed to git — deploy failed immediately; (2) default `torch` install pulled multi-GB CUDA/NVIDIA packages unneeded on CPU-only hosting — fixed with `--extra-index-url .../whl/cpu`; (3) the gitignored `chroma_db/` didn't exist on the fresh server, crashing before `uvicorn` could bind a port — fixed by making the collection **self-healing** (`_build_collection_if_empty()` rebuilds from `days/*.md` if empty); (4) loading `torch`/`transformers` + embedding ~624 chunks exceeded Render free tier's 512MB RAM — fixed by switching to Hugging Face's **hosted** Inference API for embeddings (no local model at all), dropping 122→86 dependencies.
- **Lesson:** "works on my machine" quietly depends on things that don't exist elsewhere — an ignored file, unlimited local RAM, or "a full ML stack is free to load." Each fix here (git-track the file, respect memory limits, prefer a hosted API over a local model under constraints) is a transferable production skill.

### Frontend + Keeping RAG In Sync (Day 30)

- Added a plain-HTML `/chat` route (inline string, no build step) calling the existing `POST /ask` — turned an API-only demo into a clickable product.
- Discovered the **local** `chroma_db` was stale (built once ~Day 14-16, never rebuilt) because the self-healing "rebuild if empty" check only guards against *complete absence* of data, not *staleness* — Days 17-29 notes were invisible to local retrieval even though the deployed version (which rebuilds fresh on every Render redeploy) already had them.
- **Lesson:** "empty" and "outdated" are different failure modes for any lazily-populated cache/database — a rebuild-if-empty check does not protect against staleness; that needs its own explicit check (e.g. a content hash or file count comparison).

---

## Days 40–42 — Embedding Swap, Threshold Tuning, Grounding Check

### Switching The Embedding Provider (Day 40)

- **Same model, same space.** Each embedding model learns its own private coordinate system. Different dimension (384 vs 768) fails loudly (Chroma dimension error); same dimension but different model fails *silently* with garbage distances — the dangerous case. Chunks and queries must come from one model.
- Chunking is independent of the embedding model. 768 is the **output** size (default is 3072, set `output_dimensionality`); the **input** limit is 2,048 tokens.
- `task_type` labels how a vector will be used: `RETRIEVAL_DOCUMENT` for stored chunks, `RETRIEVAL_QUERY` for the question.
- Free tier = 100 embed texts/min, so embed **offline** once (`ingest.py` -> `embeddings.json`), ship the file, load it into Chroma at startup with no API calls. Retry with exponential backoff only for 429/5xx.
- **Lesson:** build-time work belongs at build time; startup rebuilds burn quota and stall deploys.

### Measuring A Threshold, Not Guessing It (Day 41)

- A relevance threshold belongs to **one embedding model's distance scale** — 0.75 (MiniLM) let everything through on Gemini; re-measure after any model change.
- **Threshold sweep:** label questions by what *should* happen (answer / refuse) before looking at distances, collect the best distance once, then count **false refusals** (good question refused) and **false answers** (bad question answered) per threshold. 0.35 had the fewest total mistakes.
- **Distance measures topical similarity, not whether a chunk can answer the question** — "how does LoRA work" is close to notes about model training. No threshold can separate "covered" from "adjacent topic".
- A broken *measuring tool* is not a broken app: the eval needed a 15 s `finally: time.sleep` so the Day 38 rate limit (5 req/60 s) wouldn't turn healthy answers into failures.
- Before loosening an eval criterion, check the answer is actually correct; loosening can let wrong answers pass.

### Grounding Check — Verify In Code, Not In The Prompt (Day 42)

- **Provenance** = where information came from. The bug was wrong provenance: an answer from model memory labelled with note files as sources. "Answer only from the context" in a prompt is a request, not a guarantee.
- **Fix:** the model returns JSON `{"answer", "quote"}` (quote = one sentence copied exactly from the context; empty strings if the notes lack the answer). Code checks `quote_in_context`; missing/empty/invalid -> refuse. The quote is never shown to the user.
- **Fail closed:** when a check cannot be completed or fails, refuse. Invalid JSON, wrong types, empty answer, quote not found -> "No relevant notes found".
- The check proves the quote **exists** in the retrieved text, not that it **supports** the answer. A real but irrelevant quote passes. Next layers: answer-vs-quote word overlap, embedding similarity, or an LLM judge.
- **Normalize before comparing:** lowercase and keep only letters/digits, so markdown (`**Temperature:**`) and punctuation cause no false rejections. Too strict = false refusals.
- **Empty-string trap:** `"" in text` is `True`, so check for an empty quote first or it passes (fails open).
- **Defensive parsing:** `json.loads` raises on junk, and valid JSON can still be a list or have non-string fields; return `None`, never crash.
- **Chat completion call, anatomy:** `client.chat.completions.create(model=..., temperature=..., messages=[...])`. Each message is `{"role": "system|user|assistant", "content": "..."}`; system = standing instructions, user = the question. The reply text is `response.choices[0].message.content`. An f-string only works if the variables it names exist.
- **Python:** strings are immutable (`text.lower()` returns a new string — assign it); `a = b` shares one object, `dict(b)` makes a shallow copy.
- **Deployment boundary:** Render ships only `projects/day-27/awesome-project/`, so helper code must be copied into `assistant.py`, never imported from another day's folder.

---

## Repo Assistant — Current Architecture (as of Day 42)

```
User question (CLI or /chat web UI or POST /ask)   [input length cap + per-IP rate limit, 5 req/60 s]
    ↓
model_plan_action() — Groq llama-3.1-8b-instant, temperature=0
    ↓ (routes to one of, validated against ALLOWED_ACTIONS, falls back to rule-based plan_action on invalid output)
    ├── answer_question()      → TTL cache → retrieve_chunks() [Gemini embeddings, precomputed vectors loaded from embeddings.json → ChromaDB cosine search]
    │                            → distance gate (0.35) → Groq generation returning JSON {answer, quote}
    │                            → parse_answer() + quote_in_context() → cited answer, or "No relevant notes found" (fail closed)
    ├── check_git_status()     → `git status --short` on the repo
    └── read_progress_files()  → reads progress.md directly (avoids RAG hallucination for "what day am I on" style questions)
```

Deployed live on Render (`repo-assistant-api`); the ChromaDB collection is rebuilt at startup from `embeddings.json` (no API calls — re-run `ingest.py` and re-commit the file when notes change), FastAPI backend + plain HTML `/chat` frontend with 👍/👎 feedback.

**Known open gaps (as of Day 42):** the live eval (Day 31) still needs the LoRA/GPT-4 should-refuse cases and a wider Q1 keyword; the quote check proves existence, not support; `ingest.py` has no staleness check.
