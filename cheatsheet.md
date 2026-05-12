# AI Concepts Cheat Sheet

Quick-reference glossary of every concept learned so far. Use this for fast revision — each entry is 1-2 lines with a link to the full explanation.

Last updated: Day 06

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
