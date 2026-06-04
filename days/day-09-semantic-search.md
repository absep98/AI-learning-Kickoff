# Day 09 — Semantic Search (Embedding-Based Retrieval)

> Previous: [Day 08 — Terminal Chatbot](day-08-terminal-chatbot.md)

## What This Day Is About

Built a semantic search engine from scratch — a system that finds documents by **meaning**, not keywords. This is the retrieval half of RAG. Zero keyword overlap between queries and results, yet the ranking still works.

---

## 1. What Was Built

A Python script (`projects/day-09-semantic-search/search.py`) that:
- Stores 10 hardcoded "documents" (short sentences about Go, databases, and AI)
- Embeds all documents at startup using all-minilm via Ollama
- Takes a query in a loop
- Embeds the query with the same model
- Computes cosine similarity between query vector and every document vector
- Prints the top 3 most relevant documents ranked by score

### The results that prove it works

```
Query: "how do I run tasks in parallel in Go"
  0.5629  Goroutines are lightweight threads managed by the Go runtime.
  0.4299  Go's garbage collector is concurrent and low-latency.
  0.2508  Channels are how goroutines communicate safely.

Query: "what is fast caching"
  0.4261  Redis is an in-memory key-value store often used as a cache.

Query: "how do LLMs understand meaning"
  0.2234  Embeddings convert text into vectors that encode meaning.
  0.2219  A transformer uses attention to weigh relationships between tokens.
```

**None of the queries share keywords with their top results.** "parallel" is not in the goroutines doc. "caching" is not in the Redis doc (it says "cache"). "understand meaning" is not in the embeddings doc. Yet the ranking is correct every time.

This is the difference between keyword search and semantic search.

---

## 2. How It Works — The 5-Step Flow

```
STARTUP (once):
  10 documents → embed each with all-minilm → store vectors in memory

EACH QUERY:
  1. User types a question
  2. Embed the question with the SAME model (all-minilm)
  3. Compute cosine similarity between query vector and every doc vector
  4. Sort by score (descending)
  5. Print top 3
```

### Why the same model matters

The query and documents MUST be embedded by the same model. Different models produce vectors in different spaces — comparing them would be like measuring one distance in miles and another in kilograms.

### Why we embed docs only once

Documents don't change. Embed them at startup, store the vectors, query many times. This is exactly how production vector databases work — you embed once, query millions of times.

---

## 3. New Concept — Pooling (How a Sentence Becomes One Vector)

This was a question that came up during the build: "We learned that transformers process token-by-token and produce a vector per token. So why did Ollama give us ONE vector for a whole sentence?"

### The answer: Pooling

When you send a sentence to all-minilm, internally it does everything we learned:

```
Step 1: Tokenize
  "Goroutines are lightweight" → ["Go", "##rout", "##ines", "are", "lightweight"]

Step 2: Embed + Self-Attention
  Each token gets its own 384-dimensional vector
  Self-attention enriches each vector with context from all other tokens
  Result: a 5 × 384 grid (one vector per token)

Step 3: Pooling (THE NEW STEP)
  Compress the 5 token vectors into 1 sentence vector
  → This is what the API returns
```

### Two common pooling methods

**Mean Pooling:** Average all token vectors together. If you have 5 vectors of 384 dimensions, you get 1 vector of 384 dimensions where each dimension is the average across all 5 tokens. This is what most embedding models use.

**CLS Token:** Some models insert a special `[CLS]` token at the start of the sentence. Because of self-attention, by the time processing finishes, this token has "listened" to every other word and absorbed the entire sentence's meaning. The model returns only this one vector and throws away the rest.

### Why this matters — embedding models vs generation models

| Use Case | Internal Processing | Final Output |
|---|---|---|
| **Embedding / Search** | Token-by-token → Self-Attention → **Pooling** | One single vector for the whole text |
| **Text Generation (ChatGPT)** | Token-by-token → Self-Attention → **Next Token Prediction** | A stream of new tokens, one after another |

Both use the same transformer architecture internally. The difference is the **final step**:
- Embedding models **pool** all token vectors into one "fingerprint" vector
- Generation models take the **last token's** vector and predict the next token ID

This connects two things that seemed separate:
- Day 07's embedding demo (one vector per word) → actually pooling a one-word sentence
- Day 08's streaming chatbot (token-by-token output) → the generation path, no pooling

---

## 4. Code Breakdown

```python
# Documents: the "knowledge base" to search
documents = [
    "Goroutines are lightweight threads managed by the Go runtime.",
    "Redis is an in-memory key-value store often used as a cache.",
    ...
]
```

```python
# Embed all docs at startup — one API call per doc
embeddings = {}
for document in documents:
    resp = requests.post(OLLAMA_URL, json={"model": MODEL, "input": document})
    vector = resp.json()["embeddings"][0]
    embeddings[document] = vector
```
Each doc becomes a 384-dimensional vector. Stored as a dict mapping `doc_text → vector`.

```python
# Cosine similarity — reused from embedding_demo.py
def cosine_similarity(vec_a, vec_b):
    dot = sum(a*b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a*a for a in vec_a))
    mag_b = math.sqrt(sum(b*b for b in vec_b))
    return dot / (mag_a * mag_b)
```

```python
# Query loop
while True:
    query = input()
    if query == 'quit':
        break

    # Embed the query with the SAME model
    query_resp = requests.post(OLLAMA_URL, json={"model": MODEL, "input": query})
    query_vector = query_resp.json()["embeddings"][0]

    # Score every doc against the query
    results = []
    for doc, doc_vector in embeddings.items():
        score = cosine_similarity(query_vector, doc_vector)
        results.append((doc, score))

    # Sort and show top 3
    results.sort(key=lambda x: x[1], reverse=True)
    for doc, score in results[:3]:
        print(f"  {score:.4f}  {doc}")
```

---

## 5. What This Is vs What RAG Will Be

```
Semantic search (Day 09)          RAG (Day 10)
────────────────────────          ──────────────────────────────
Embed docs at startup        →    same
Embed query                  →    same
Cosine similarity            →    same
Print top 3 results          →    send top 3 to chatbot as context
                             →    chatbot generates answer FROM them
```

RAG is literally this search + the chatbot from Day 08. Take the top results, inject them into the system prompt or user message, and let the LLM generate a grounded answer. That's it.

---

## 6. What This Proves

### Keyword search is dead for AI

Searching for "parallel tasks" and finding "goroutines" is impossible with keyword matching. Semantic search makes this trivial.

### Embeddings capture meaning, not spelling

"caching" and "cache" aren't identical strings. But their embeddings are close because the meaning is the same. This is why Day 07's cosine similarity demo matters — it's the foundation for real retrieval.

### The ranking is meaningful

Scores are not binary (match/no-match). They're a gradient:
- 0.56 = strong match (goroutines for "parallel in Go")
- 0.43 = related (GC for "parallel" — both about concurrency)
- 0.25 = weak match (channels — related but less directly)
- Below 0.15 = unrelated

### This is production-grade retrieval logic

Real vector databases (Pinecone, Weaviate, ChromaDB) do exactly this — store embeddings, accept a query embedding, return top-K by cosine similarity. The only difference is scale (millions of docs vs our 10) and optimization (approximate nearest neighbor algorithms vs our brute-force loop).

---

## Key Takeaways

**Semantic search finds by meaning, not keywords.** "parallel tasks" matches "goroutines" because the vectors are close, even with zero word overlap.

**Embed once, query many times.** Documents are embedded at startup. Only the query is embedded per request. This is how production systems work.

**Same model on both sides.** Query and documents must use the same embedding model, or the vector spaces don't match.

**Pooling is the bridge.** Embedding models use pooling (mean or CLS) to compress per-token vectors into one sentence vector. Generation models use next-token prediction instead. Same transformer, different final step.

**This is the retrieval half of RAG.** Day 10 connects these search results to the chatbot — and that's a complete RAG system.

---

## One-Line Summaries

**Semantic search:** Embed documents and queries with the same model, rank by cosine similarity — finds results by meaning, not keywords.

**Pooling:** The extra step where an embedding model compresses all per-token vectors into one sentence vector, so you get a single "fingerprint" for the whole text.

**Embed once, query many:** Documents are static, embed at startup. Only the query changes per request.

**Same model rule:** Query and documents must use the same embedding model — different models = different vector spaces = garbage scores.

---

## Revision Questions

1. **Your query is "how do I run tasks in parallel" and the top result is about goroutines. These share zero keywords. How did it work?**
2. **Why must the query and documents be embedded by the same model?**
3. **You embed 10 documents at startup. The user asks 100 questions. How many embed API calls happen total?**
4. **What is pooling? Why does the embedding API return one vector per sentence instead of one per token?**
5. **Name the two common pooling methods and explain the difference.**
6. **An embedding model and a generation model both use transformers internally. What is the difference in their final step?**
7. **You search for "database" and get PostgreSQL (0.45) and Redis (0.42). Why does PostgreSQL rank higher even though Redis is also a data store?**
8. **What would happen if you embedded documents with all-minilm but embedded queries with phi3:mini?**
9. **You have this semantic search working. What ONE change turns it into RAG?**
10. **A production vector database stores 10 million documents. Does it re-embed all of them on every query? Why not?**
