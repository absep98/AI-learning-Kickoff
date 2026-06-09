# Day 11 — RAG Over Real Notes (Searching Your Own Learning Content)

> Previous: [Day 10 — RAG System](day-10-rag.md)

## What This Day Is About

Upgraded the Day 10 RAG from 10 hardcoded sentences to **467 real chunks from 10 days of learning notes**. The system now searches your actual `days/*.md` files and answers questions from them. This introduces the most important production RAG concept: **chunking**.

---

## 1. What Was Built

A Python script (`projects/day-11-rag-over-notes/rag_notes.py`) that:
- Reads all `.md` files from `days/`
- Splits each file into paragraphs (chunking by blank line)
- Filters out chunks shorter than 80 characters (removes headings and dividers)
- Embeds all 467 chunks using all-minilm at startup
- Takes queries in a loop and answers from the retrieved chunks

### Results

```
You: what is cosine similarity?
AI: Cosine Similarity measures the angle between two vectors, indicating
    their directional likeness rather than focusing on vector magnitude...
    ← answered from your Day 03/09 notes ✅

You: how does statelessness work in LLMs?
AI: In LLMs, every request initiates a new process without retaining
    information from previous interactions, making them 'stateless'...
    ← answered from your Day 05/08 notes ✅

You: what temperature should I use for coding?
AI: Lowest acceptable range is 0.1°C...
    ← WRONG — retrieval missed the temperature guide ❌
```

The third answer is a retrieval failure — the relevant chunks from Day 02's temperature guide weren't retrieved. This is the most important lesson of the day.

---

## 2. The New Concept — Chunking

### What chunking is

Chunking = splitting large documents into smaller searchable pieces before embedding.

In Day 10, your "documents" were 10 short sentences — already the right size. In Day 11, each `.md` file is 100–450 lines. You can't embed an entire file as one vector because:

1. **Context window limit** — all-minilm truncates inputs at ~256 tokens. A 400-line file gets silently cut off. The vector only represents the first chunk.
2. **Signal dilution** — one vector for an entire file "means" everything in it. Searching for "cosine similarity" won't distinguish between the Day 03 file (heavily about cosine similarity) and the Day 05 file (briefly mentions it among 20 other topics).
3. **Retrieval precision** — you want to retrieve the specific paragraph about cosine similarity, not the whole file it lives in.

### Chunking strategy used

**Split by paragraph (blank line boundary):**
```python
paragraphs = content.split("\n\n")
```

This is the simplest strategy. Each paragraph becomes one chunk. One chunk = one vector = one searchable unit.

### Why filter short chunks

After splitting, many chunks are markdown artifacts:
```
## Temperature          ← 15 chars, no searchable meaning
---                     ← 3 chars
| Day | Topic |         ← table header
```

Filtering `len(chunk) > 80` cuts 994 → 467 chunks with minimal real content loss. Real explanations and definitions are almost always longer than 80 characters.

### The chunking tradeoff

| Chunk too large | Chunk too small |
|---|---|
| Signal diluted | Context lost (no surrounding info) |
| Embedding truncated | More API calls, slower startup |
| Less precise retrieval | Single sentences may not embed well |

Paragraph-level chunking is a good middle ground for note-style documents.

---

## 3. The Startup Problem — 467 Embeddings Takes Time

With 10 documents (Day 10): instant startup.  
With 467 chunks (Day 11): ~8-10 minutes on CPU.

This is the core reason production systems use **persistent vector databases**:
- Embed once, save to disk
- Next run: load vectors from disk, skip embedding
- Only re-embed when documents change

Tools like ChromaDB, Weaviate, and Pinecone do exactly this. For now, we embed on every run — acceptable for learning, not for production.

```python
# Progress indicator so you know it's working
for i, document in enumerate(documents):
    resp = requests.post(OLLAMA_URL_EMBEDDING, ...)
    if i % 50 == 0:
        print(f"Embedding chunk {i}/{len(documents)}...")
```

---

## 4. Retrieval Quality — Why the Temperature Answer Was Wrong

The query was "what temperature should I use for coding?" The model answered about physical temperature (0.1°C). This happened because:

1. The retrieved chunks didn't contain the Day 02 temperature guide
2. The model received irrelevant context
3. With no good context, it hallucinated a plausible-sounding but wrong answer

**Key insight: In RAG, bad answers = bad retrieval.** When a RAG system gives a wrong answer, the first place to debug is the retrieval step, not the generation step. Ask: "Did the right chunks get retrieved?"

### Why the retrieval missed

Possible reasons:
- The temperature guide in Day 02 uses the word "temperature" in an AI-specific context. The query also says "temperature" but the surrounding words ("coding", "use for") match all-minilm's understanding of physical temperature better
- The relevant chunks may have been filtered out (< 80 chars) if the practical guide was formatted as a short table row
- Paragraph splitting may have broken the temperature table into rows, each too short to survive the filter

### The fix pattern for retrieval misses

1. **Lower the chunk filter threshold** — try 40 chars instead of 80
2. **Retrieve more chunks** — top 5 instead of top 3 gives more surface area
3. **Improve the query** — "what temperature value should I set for LLM code generation?" is more specific
4. **Check what was retrieved** — print `result[:3]` with scores to see what the model actually received

---

## 5. Code Additions vs Day 10

Day 11 adds exactly one new function to Day 10's code:

```python
def load_chunks(folder_path):
    chunks = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".md"):
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as file:
                content = file.read()
            paragraphs = content.split("\n\n")
            chunks.extend([p.strip() for p in paragraphs if p.strip() and len(p.strip()) > 80])
    return chunks
```

Everything else — embedding loop, cosine similarity, query loop, context injection, LLM call — is identical to Day 10. The only change is the source of documents: hardcoded list → real files.

---

## 6. What This Is vs Production RAG

| | Day 11 (this) | Production RAG |
|---|---|---|
| Document source | `days/*.md` files | PDFs, databases, wikis, APIs |
| Chunking | Split by `\n\n` | Overlapping chunks, semantic splitting |
| Chunk filter | > 80 chars | More sophisticated relevance filtering |
| Embeddings | Re-computed every run | Persisted in vector database |
| Retrieval | Brute-force cosine loop | Approximate nearest neighbor (ANN) |
| Scale | 467 chunks | Millions of chunks |
| Startup time | 8-10 minutes | Milliseconds (pre-computed) |

The architecture is identical. The engineering challenges at scale are different.

---

## Key Takeaways

**Chunking is the most important RAG engineering decision.** Too large = signal dilution and truncation. Too small = context loss and noise. Paragraph-level splitting is a solid starting point.

**Filter meaningless chunks.** Markdown headings, dividers, and table separators waste embedding calls and add retrieval noise. A minimum length filter removes them.

**Bad RAG answers = bad retrieval, not bad model.** Debug retrieval first: print the retrieved chunks and their scores. If the right content isn't retrieved, the model can't answer correctly even if it's GPT-4.

**Persistent vector storage is the production solution to startup time.** Embed once, save to disk, load on next run. We skip this for now but it's the next natural step.

**RAG quality is an engineering problem.** Chunking strategy, chunk size, filter threshold, number of retrieved chunks, query phrasing — all of these affect answer quality. It's not magic.

---

## One-Line Summaries

**Chunking:** Splitting large documents into paragraph-sized pieces so each chunk embeds as a focused, searchable unit of meaning.

**Chunk filter:** Remove chunks shorter than a threshold to eliminate markdown artifacts that add noise without adding meaning.

**Retrieval miss:** When RAG gives a wrong answer, the retrieved chunks were wrong — debug retrieval, not generation.

**Persistent embeddings:** The production fix for slow startup — embed once, save vectors to disk, reload on next run.

---

## Revision Questions

1. **Why can't you embed an entire 400-line markdown file as one vector?** *(Two reasons)*
2. **What is the chunking strategy used in this script? What are its limitations?**
3. **You have 467 chunks and startup takes 8 minutes. What is the production solution?**
4. **The model gave a wrong answer about temperature. How do you debug a RAG retrieval miss?**
5. **Why do we filter chunks shorter than 80 characters? What gets removed? What might we miss?**
6. **You lower the filter from 80 to 40 characters. What is the tradeoff?**
7. **Your RAG answers "I don't know" to a question you know is in your notes. Name 3 possible causes.**
8. **What is the only new function in Day 11 vs Day 10? What does it do?**
9. **Paragraph splitting broke a markdown table into single-row chunks. Why is this bad for retrieval?**
10. **Name 3 differences between your Day 11 RAG and a production RAG system.**
