# Day 07 — The Pipeline Made Real (Tokenization + Embeddings Hands-On)

> Previous: [Day 06 — Hands-On Ollama Experiments](day-06-hands-on-ollama-experiments.md)

## What This Day Is About

Days 1–6 explained the LLM pipeline as theory. Today I ran **Step 1 (Tokenize)** and **Step 2 (Embed)** as actual Python code on my machine and proved the concepts work exactly as described.

This day also started with a **revision test on Day 01 questions** — which exposed gaps I thought were fixed but weren't. The hands-on experiments then made those concepts stick permanently.

---

## 1. Revision Test Results — What I Still Got Wrong

I attempted the Day 01 revision questions without looking at notes. Results:

| Area | Verdict |
|---|---|
| LLM core (predict next token) | Pass — but was saying "word" instead of "token" |
| Token ratio | **Wrong** — had the ratio backwards (said 1 token = 0.75 word instead of 1 word ≈ 1.33 tokens) |
| 5-step pipeline | **Wrong** — confused training with inference, listed attention as separate from transformer |
| Attention mechanism | Pass |
| Why LLMs feel intelligent | Too shallow — only said "lots of data" |
| Hallucination | Pass |
| Cost calculation | **Wrong** — used inverted ratio, missed output tokens costing 2-4x more |

**Key lesson:** Reading notes ≠ understanding. I "knew" the pipeline from Day 03 corrections, but couldn't reproduce it under pressure. The fix was running real code.

---

## 2. Step 1 — Tokenization (Real Code)

### What I ran

Used `tiktoken` (OpenAI's tokenizer library) to split text into actual tokens.

### Tool
```
pip install tiktoken
```

### Code pattern
```python
import tiktoken
enc = tiktoken.get_encoding("cl100k_base")  # GPT-4's tokenizer
tokens = enc.encode("The cat sat")
# Result: [791, 8415, 7731]
# Pieces: ['The', ' cat', ' sat']
```

### What I proved

**Simple English — 1:1 ratio:**
```
"The quick brown fox jumps over the lazy dog"
  Words: 9, Tokens: 9, Ratio: 1.00 tokens/word
```

**Code — 2.2x ratio:**
```
"def calculate_average(numbers: list[int]) -> float:"
  Words: 5, Tokens: 11, Ratio: 2.20 tokens/word
```

**Hindi (non-English) — 3.4x ratio:**
```
"मैं AI सीख रहा हूं"
  Words: 5, Tokens: 17, Ratio: 3.40 tokens/word
```

**Subword splitting:**
```
"unhappiness" → ['un', 'h', 'appiness']  (1 word = 3 tokens)
"getUserById(id):" → ['def', ' getUser', 'ById', '(id', '):']  (1 "word" = 5 tokens)
```

### What this proves

1. Tokens are NOT words — they are subword pieces
2. Code uses ~2x more tokens than English (symbols, camelCase splitting, brackets all become separate tokens)
3. Non-English languages are expensive (tokenizer was trained primarily on English)
4. The 1 word ≈ 1.33 tokens rule is an average — actual ratio depends on content type

---

## 3. Step 2 — Embeddings (Real Code)

### What I ran

Used Ollama with `all-minilm` (a dedicated embedding model, 45MB) to convert words into vectors and measure their similarity.

### Why not phi3:mini?

phi3:mini is a **chat model** — trained to predict the next token. It has an embedding layer internally, but those vectors were never optimized for similarity comparison. When forced to produce embeddings:
- "cat" vs "kitten" = 0.16 (should be high)
- "cat" vs "car" = 0.99 (should be low)
- Complete nonsense results

`all-minilm` is an **embedding model** — trained specifically so that similar meaning = similar vectors. Different tool, different job.

### Tool
```
ollama pull all-minilm
```

### Code pattern
```python
import requests
resp = requests.post("http://localhost:11434/api/embed", 
    json={"model": "all-minilm", "input": "cat"})
vector = resp.json()["embeddings"][0]
# Result: 384 numbers like [0.0373, 0.0512, -0.0003, ...]
```

### What I proved — Cosine Similarity Results

```
"car" vs "automobile"              → 0.86  (same meaning, different word — HIGH)
"cat" vs "kitten"                  → 0.79  (very related — HIGH)
"cat" vs "dog"                     → 0.66  (both animals — MEDIUM)
"cat" vs "car"                     → 0.46  (unrelated — LOW)
"cat" vs "python programming"      → 0.24  (totally unrelated — VERY LOW)
```

### What this proves

1. Embeddings capture **meaning**, not spelling — "car" and "automobile" are close despite zero letters in common
2. Similarity is a gradient, not binary — "cat/kitten" > "cat/dog" > "cat/car" > "cat/python"
3. This is exactly how **semantic search** works — search for "automobile" and find documents about "cars"
4. This is the **retrieval step in RAG** — embed the query, find closest document chunks by cosine similarity

---

## 4. Two Types of Models — Crucial Distinction

| | Chat/Generation Model | Embedding Model |
|---|---|---|
| **Example** | phi3:mini, GPT-4, Gemini | all-minilm, text-embedding-ada-002 |
| **Trained for** | Predicting next token | Making similar text → similar vectors |
| **Output** | Generated text (tokens) | A vector of numbers |
| **Can generate text?** | Yes | No |
| **Can compare meaning?** | Poorly | Extremely well |
| **Size** | Large (2–400GB) | Small (45MB–1GB) |
| **Used in RAG for** | Generation step (answer the question) | Retrieval step (find relevant docs) |

**In a RAG system, you use BOTH:**
1. Embedding model finds relevant documents (semantic search)
2. Chat model generates a response using those documents

---

## 5. Steps 3–5 — Why We Can't Run Them

| Step | What it does | Why we can't inspect it |
|---|---|---|
| 3. Transformer + Attention | Tokens "look at" each other, enrich their vectors with context | Happens across billions of parameters inside the neural network |
| 4. Probabilities | Output distribution over all possible next tokens | Internal computation — we only see the final picked token |
| 5. Sampling | Pick one token from the distribution (temperature applies here) | We see the result but not the distribution |

These steps happen inside the model weights. We send text in and get text out — the middle is a black box unless you build your own transformer from scratch (not our goal).

**What we CAN observe about steps 3–5:**
- Temperature changes output variety (Step 5 — proved on Day 04)
- Longer input = slower response (Step 3 — attention cost is n², proved on Day 06)
- Same prompt → different outputs (Step 5 — sampling is probabilistic, proved on Day 04)

---

## 6. The Complete Picture — Pipeline with Real Tools

```
YOUR INPUT: "What is a goroutine?"

Step 1 - TOKENIZE (tiktoken)
    "What is a goroutine?" → [3923, 374, 264, 7160, 28975, 30]
    6 tokens

Step 2 - EMBED (all-minilm / internal embedding layer)
    Each token ID → 384-dimensional vector
    [3923] → [0.04, -0.02, 0.11, ...]
    [374]  → [-0.03, 0.08, 0.01, ...]
    ...

Step 3 - TRANSFORMER + ATTENTION (black box)
    All 6 vectors processed simultaneously
    Each token attends to all others
    "goroutine" gets enriched with context from "What is"
    Multiple layers of this (32+ layers in phi3:mini)

Step 4 - PROBABILITIES
    Final vector → probability over 32,000 possible next tokens
    "A" → 22%, "In" → 15%, "Gor" → 8%, ...

Step 5 - SAMPLING
    Temperature 0.7 → picks "A"
    Output: "A"

Then repeat from Step 1 with "What is a goroutine? A" as input...
→ "A goroutine is a lightweight..."
→ Each new token = full pipeline pass
```

---

## Key Takeaways

- **Tokenization is mechanical and inspectable.** You can run it yourself and see exactly how text splits. No mystery.
- **Embeddings are real numbers with real meaning.** Similar concepts produce close vectors. Different concepts produce far vectors. This powers all of semantic search and RAG.
- **Chat models ≠ embedding models.** Different training objectives, different capabilities. RAG uses both.
- **Revision exposed gaps that "reading notes" didn't fix.** Running real code made the pipeline concrete in a way that re-reading never did.
- **Steps 3–5 are a black box** but their effects are observable through temperature experiments, speed tests, and non-deterministic outputs.

---

## One-Line Summaries

**Tokenization (real):** `tiktoken` splits text into subword pieces — code uses 2x more tokens, non-English uses 3x more.

**Embeddings (real):** A 384-dimension vector where similar meaning = close vectors — "car" and "automobile" score 0.86 despite sharing no letters.

**Embedding model vs chat model:** Embedding models measure meaning-similarity. Chat models generate text. RAG needs both.

**Cosine similarity (proved):** The similarity gradient cat/kitten (0.79) > cat/dog (0.66) > cat/car (0.46) matches human intuition perfectly.

**Pipeline made tangible:** Steps 1–2 are inspectable code. Steps 3–5 are black-box neural computation whose effects we observe indirectly.

---

## Revision Questions

1. **What does tiktoken do? Can it generate text?**
2. **"getUserById(id):" becomes 5 tokens. List what they likely are and explain why code is expensive.**
3. **Why does Hindi use 3.4 tokens per word while English uses ~1.0?**
4. **What is an embedding model? How is it different from a chat model?**
5. **You used phi3:mini for embeddings and got nonsense. Why? What did you switch to and why did it work?**
6. **"car" vs "automobile" = 0.86 similarity. These words share zero letters. How is this possible?**
7. **In a RAG system, which model handles retrieval and which handles generation?**
8. **Why can't we inspect Steps 3–5 the way we inspected Steps 1–2?**
9. **Name 3 things you can observe that prove Steps 3–5 are working** (even though you can't see inside).
10. **You got the pipeline wrong on revision. What was the mistake and what's the correct 5-step sequence?**
