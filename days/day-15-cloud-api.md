# Day 15 — Cloud API (Groq + Llama replacing local phi3:mini)

> Previous: [Day 14 — ChromaDB Vector Database](day-14-chromadb.md)

## What This Day Is About

Swapped the local phi3:mini generation model for a cloud API (Groq running Llama 3.1 8B). Same ChromaDB retrieval, same all-minilm embeddings, same chunking — only the generation step changed. The result proved the core lesson: **retrieval quality and generation quality are independent problems**.

---

## 1. The Result That Proves It

**Same retrieval, same chunks, completely different answer quality:**

| Query | phi3:mini (local, Day 14) | Llama 3.1 8B via Groq (Day 15) |
|---|---|---|
| "what temperature for coding?" | "low to medium around [90%, 5%]" ❌ | "0.1–0.3, promotes deterministic predictions" ✅ |
| "what is cosine similarity?" | Correct but vague | "directional similarity regardless of vector length" ✅ |

The temperature query was failing for days because phi3:mini misread a probability table. Llama 3.1 8B reads the same table and extracts the correct specific value.

---

## 2. What Changed — One Section of Code

Everything from Day 14 is identical. The only change is the generation call:

### Before (phi3:mini via Ollama)
```python
response = requests.post(
    "http://localhost:11434/api/chat",
    json={"model": "phi3:mini", "messages": conversation_history, "stream": False}
)
full_response = response.json()["message"]["content"]
```

### After (Llama 3.1 8B via Groq)
```python
from groq import Groq

groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])

response = groq_client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": "Answer only from context. JSON only: {\"answer\": \"...\", \"confidence\": \"...\"}"},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
    ]
)
full_response = response.choices[0].message.content.strip()
```

**Lines changed: ~8.** Everything else — ChromaDB query, chunk filtering, source tracking, JSON parsing — unchanged.

---

## 3. The Full Stack Now

```
User query
    ↓
all-minilm (local, Ollama)       ← embeds the query into a 384-dim vector
    ↓
ChromaDB (local, persistent)     ← finds top 5 chunks by cosine distance
    ↓
Llama 3.1 8B (cloud, Groq)       ← generates answer from retrieved context
    ↓
JSON parsed → Answer + Confidence + Sources
```

**Exact model used:** `llama-3.1-8b-instant` on Groq. This is the specific model name passed to `groq_client.chat.completions.create(model="llama-3.1-8b-instant", ...)`.

**Exact embedding model used:** `all-minilm` via Ollama locally. Same model as Day 11/14 — unchanged.

**Why local embeddings + cloud generation?** Embeddings are cheap to run locally (all-minilm is tiny, fast, no GPU needed). Generation is where quality matters most — a large cloud model like Llama 3.1 8B reads the retrieved chunks far more accurately than a small local model. So: local embeddings for cost/privacy, cloud generation for quality.

---

## 4. API Key Management — What Went Wrong and How to Do It Right

### The mistakes made
- Stored API key in `.env` as `$env:GOOGLE_API_KEY = key` (PowerShell syntax, not `.env` syntax)
- Keys were exposed in chat
- No `.gitignore` to prevent committing secrets

### The correct `.env` format
```
GOOGLE_API_KEY=your-key-here
GROQ_API_KEY=your-key-here
```
No `$env:`, no quotes, no spaces around `=`. Just `KEY=value`.

### Loading it in Python
```python
from dotenv import load_dotenv
load_dotenv(r"C:\learning\aithings\.env")  # explicit path
```

### `.gitignore` prevents accidental commits
```
.env
__pycache__/
*.pyc
```

### Key rotation rule
If a key appears anywhere in a chat, email, or log file — **regenerate it immediately**. Keys are credentials. Treat them like passwords.

---

## 5. Groq vs Gemini vs Ollama — When to Use Each

| | Ollama (local) | Groq (cloud, free) | Gemini (cloud, free tier) |
|---|---|---|---|
| **Cost** | Free | Free tier (rate limited) | Free tier (rate limited) |
| **Speed** | Slow (CPU) | Very fast | Fast |
| **Model quality** | Small models only | Llama 3.1 8B+ | Gemini Flash/Pro |
| **Privacy** | Full | Data leaves machine | Data leaves machine |
| **Internet required** | No | Yes | Yes |
| **Best for** | Learning, offline | Production-quality free inference | Google ecosystem |
| **Format** | Custom Ollama JSON | OpenAI-compatible | Google genai SDK |

**Groq uses the OpenAI-compatible format** — `messages` array with `role/content`, `response.choices[0].message.content`. If you learn this format (which you already have), it works with OpenAI, Groq, Anthropic (mostly), and many others.

---

## 6. Groq vs xAI/Grok — Important Distinction

These are completely different companies with confusingly similar names:

| | Groq | xAI/Grok |
|---|---|---|
| **Website** | console.groq.com | console.x.ai |
| **What it is** | Fast inference provider | Elon Musk's AI company |
| **API key prefix** | `gsk_...` | `xai-...` |
| **Models** | Llama, Mixtral, Gemma | Grok models |
| **Used in Day 15** | Yes (via Groq SDK with xAI key) | Key was xAI format |

---

## 7. The Core Lesson — Retrieval and Generation Are Independent

This day's main insight, proved by experiment:

```
Bad retrieval + good model  = wrong answer (wrong chunks → model can't help)
Good retrieval + bad model  = wrong answer (right chunks → model misreads them)
Good retrieval + good model = correct answer ✅
```

When a RAG system gives wrong answers, debug in this order:
1. Print retrieved chunks — are they relevant?
2. If yes → generation model problem (upgrade model or improve prompt)
3. If no → retrieval problem (fix chunking, threshold, embedding model)

---

## Key Takeaways

**Swapping models is trivial.** Change ~8 lines of code. All the hard work (ChromaDB, chunking, embeddings) stays the same.

**Cloud models are significantly better at instruction following.** Llama 3.1 8B correctly parsed the temperature table that phi3:mini consistently misread.

**The OpenAI-compatible format is the universal standard.** Learn `messages: [{role, content}]` + `response.choices[0].message.content` once and it works across Groq, OpenAI, Anthropic (with minor changes), and many others.

**API keys are secrets.** `.env` file, `.gitignore`, explicit `load_dotenv()` path. Never paste in chat or commit to git.

**The production RAG stack:** local embeddings (cheap) + persistent vector DB (fast) + cloud generation (smart) = best of all worlds.

---

## One-Line Summaries

**Cloud API swap:** Change 8 lines — same retrieval, same ChromaDB, different generation model. Quality jumps immediately.

**OpenAI-compatible format:** `messages=[{"role": "system/user", "content": "..."}]` + `response.choices[0].message.content` — works on Groq, OpenAI, and most cloud providers.

**Retrieval vs generation independence:** Same chunks sent to phi3:mini vs Llama 3.1 8B produce completely different answer quality — retrieval and generation are separate problems.

**API key hygiene:** `KEY=value` in `.env`, load with `load_dotenv()`, exclude with `.gitignore`, rotate immediately if exposed.

---

## Revision Questions

1. **You want to swap Groq for OpenAI. What lines change in the code?**
2. **Your RAG gives a wrong answer. How do you determine if it's a retrieval problem or a generation problem?**
3. **phi3:mini misread a probability table as temperature values. Llama 3.1 8B read it correctly. Why?**
4. **What is the difference between Groq and xAI/Grok? How can you tell which key you have?**
5. **Why is the `.env` file excluded from git? What happens if you accidentally commit it?**
6. **What is `load_dotenv()` doing? Why pass an explicit path instead of just `load_dotenv()`?**
7. **Name the three components of your current RAG stack. Which runs locally and which runs in the cloud?**
8. **Groq uses the OpenAI-compatible format. What does that mean practically for your code?**
9. **You want to add streaming to the Groq call. What parameter do you add? What changes in response parsing?**
10. **A colleague says "just use the biggest model available for everything." What's wrong with this approach?**
