# Day 10 — RAG (Retrieval-Augmented Generation)

> Previous: [Day 09 — Semantic Search](day-09-semantic-search.md)

## What This Day Is About

Built a complete RAG system by combining the semantic search from Day 09 with the chatbot from Day 08. The model now answers from **your documents**, not from its training weights. This is how every serious AI product works — customer support bots, document Q&A, GitHub Copilot's codebase context.

---

## 1. The Result That Proves It Works

```
Query: "what is fast caching in databases?"

→ Retrieval found: "Redis is an in-memory key-value store often used as a cache."

→ LLM answered:
  "Based on the context provided, fast caching in databases refers to using Redis,
   which is described as an in-memory key-value store frequently utilized for its
   performance advantages..."
```

The word "Redis" never appeared in the query. The model didn't guess — it read the retrieved document and synthesized an answer from it. That's RAG.

---

## 2. What RAG Is and Why It Exists

### The problem with a plain LLM

```
User: "What is our refund policy?"
LLM: [invents a plausible-sounding policy from training data — probably wrong]
```

A plain LLM can only use what it learned during training. It has no access to your private data, your updated docs, or anything after its training cutoff.

### The RAG solution

```
User: "What is our refund policy?"
→ Search retrieves: your actual refund policy document
→ LLM receives: "Here is the refund policy: [actual text]. Answer using only this."
→ LLM answers from the document — correct, grounded, citeable
```

RAG = give the LLM the relevant facts just-in-time, in the prompt. No retraining needed.

### Why this matters more than fine-tuning

| Approach | Cost | Updatable? | Uses your docs? |
|---|---|---|---|
| Plain LLM | Free | No | No |
| Fine-tuning | High | Requires retraining | Sort of |
| **RAG** | **Low** | **Yes — add docs anytime** | **Yes — exactly your docs** |

Most production AI products use RAG, not fine-tuning.

---

## 3. How Day 09 + Day 08 = Day 10

```
Day 09 (Semantic Search)          Day 10 (RAG)
─────────────────────────         ──────────────────────────────────
Embed documents at startup   →    same
Embed query                  →    same
Cosine similarity ranking    →    same
Print top 3 results          →    inject top 3 into LLM message
                             →    send to chatbot API (Day 08 pattern)
                             →    stream response
```

**The only new thing in Day 10:** taking the search results and building a message that includes both the context AND the question, then sending it to the LLM.

---

## 4. The Complete RAG Flow

```
STARTUP (once):
  1. Define your documents (the "knowledge base")
  2. Embed every document with all-minilm
  3. Store vectors in memory

EACH QUERY:
  1. User types a question
  2. Embed the question with all-minilm (same model — mandatory)
  3. Compute cosine similarity between question vector and every doc vector
  4. Sort, take top 3 — these are the "retrieved chunks"
  5. Build the user message:
       "Use only the context below to answer.
        Context: [top 3 docs joined together]
        Question: [user's actual question]"
  6. Send to Ollama chat API with system prompt + that user message
  7. Stream the response token-by-token
```

---

## 5. Code Breakdown — The Key New Part

Everything except Step 5-6 was already written in Days 08-09. The new piece:

```python
# Step 4: retrieved chunks as a string
context = "\n".join([doc for doc, score in results[:3]])

# Step 5: inject context into the user message
user_message = f"Use only the context below to answer.\n\nContext:\n{context}\n\nQuestion: {query}"

# Step 6: fresh conversation history per query (NOT accumulated like Day 08)
conversation_history = [
    {"role": "system", "content": "You are a helpful assistant. Answer only from the provided context."},
    {"role": "user", "content": user_message}
]

# Step 7: same streaming call as Day 08
response = requests.post(
    "http://localhost:11434/api/chat",
    json={"model": "phi3:mini", "messages": conversation_history, "stream": True},
    stream=True
)
```

### Why conversation history is reset each query

In Day 08, history accumulated — each turn appended user and assistant messages, so the model could reference earlier turns.

In RAG, history is rebuilt fresh every query because:
- The context changes every query (different docs retrieved)
- Each query is independent — you want the model focused on THIS query's retrieved docs
- Accumulating old context + new context would exceed the context window quickly

---

## 6. The Two-Model Architecture

This is the first time you've used two models together in one system:

```
Query
  ↓
all-minilm (embedding model)     ← finds relevant documents
  ↓
top 3 docs
  ↓
phi3:mini (generation model)     ← synthesizes an answer
  ↓
Answer
```

**all-minilm:** tiny (45MB), fast, no text generation, only produces vectors. Used twice — once for docs at startup, once for the query.

**phi3:mini:** 2.2GB, slow, generates text. Never sees the raw document corpus — only the top 3 chunks retrieved by all-minilm.

This pattern scales to production: swap all-minilm for OpenAI's `text-embedding-3-small`, swap phi3 for GPT-4, add a real vector database — same architecture, different components.

---

## 7. RAG vs What You Built in Days 08-09

| | Day 08 Chatbot | Day 09 Search | Day 10 RAG |
|---|---|---|---|
| Takes user input | ✅ | ✅ | ✅ |
| Retrieves relevant docs | ❌ | ✅ | ✅ |
| Sends to LLM | ✅ | ❌ | ✅ |
| Streams response | ✅ | ❌ | ✅ |
| Grounded in documents | ❌ | N/A | ✅ |
| Accumulates history | ✅ | N/A | ❌ (fresh per query) |

---

## 8. What's Missing (Production RAG Would Add)

| Missing | Why it matters |
|---|---|
| **Real documents** | Hardcoded sentences — real RAG reads files, PDFs, databases |
| **Chunking strategy** | Long documents need splitting into overlapping chunks |
| **Vector database** | In-memory dict doesn't persist — Chroma, Pinecone, Weaviate for production |
| **Source citations** | Tell the user WHICH document the answer came from |
| **Fallback when no good match** | If top score is 0.15, say "I don't have relevant info" instead of guessing |
| **Conversation memory** | This RAG forgets previous turns — real products combine RAG + history |

---

## Key Takeaways

**RAG = retrieval + generation.** Find the relevant facts first, then let the LLM synthesize an answer from them.

**The LLM is the synthesis engine, not the knowledge store.** Your documents are the source of truth. The LLM's job is to turn retrieved text into a clear answer.

**Context injection is the bridge.** The retrieved chunks go into the user message alongside the question. The LLM reads both and answers from the context, not its weights.

**Two models, two jobs.** Embedding model finds relevant docs. Generation model writes the answer. Neither can do the other's job well.

**RAG beats fine-tuning for most use cases.** Cheaper, updatable, uses exact documents, no retraining required.

---

## One-Line Summaries

**RAG:** Retrieve relevant document chunks via semantic search, inject them into the LLM prompt, get an answer grounded in your data.

**Context injection:** `f"Context:\n{retrieved_docs}\n\nQuestion: {query}"` — the entire RAG "magic" is this string formatting.

**Two-model architecture:** all-minilm finds the right docs, phi3:mini writes the answer. Different models, different jobs, one pipeline.

**Fresh history per query:** Unlike a chatbot, RAG rebuilds conversation history each time because retrieved context changes per query.

---

## Revision Questions

1. **What problem does RAG solve that a plain LLM cannot?**
2. **Draw the complete RAG pipeline from startup to answer.** *(At least 7 steps)*
3. **Why is history reset each query in RAG, but accumulated in the Day 08 chatbot?**
4. **Which model does the retrieval in your RAG system? Which does the generation? Why can't one model do both?**
5. **You ask "what is fast caching?" and the model answers about Redis. Redis was never mentioned in your query. Explain step by step how it got there.**
6. **What goes inside the `user_message` string? Why both context AND question?**
7. **RAG vs fine-tuning — when would you choose each?**
8. **Your knowledge base has 10 documents. You ask 50 questions. How many times does all-minilm run total?**
9. **What would happen if the top retrieved doc has a cosine score of 0.08? Should the model still answer from it?**
10. **You want to build a chatbot that answers questions about your company's internal docs. Describe the RAG setup: what are your documents, how do you chunk them, what embedding model, what generation model?**
