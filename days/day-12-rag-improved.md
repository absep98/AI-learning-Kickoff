# Day 12 — RAG Improved (Persistent Cache, Source Tracking, Retrieval Debugging)

> Previous: [Day 11 — RAG Over Real Notes](day-11-rag-over-notes.md)

## What This Day Is About

Three production-quality improvements to the Day 11 RAG system:
1. **Persistent embeddings** — embed once, save to disk, load instantly on every subsequent run
2. **Source tracking** — know which file each retrieved chunk came from
3. **Retrieval debugging** — print retrieved chunks with scores to diagnose wrong answers

These are not new AI concepts — they are engineering improvements that turn a learning prototype into a usable tool.

---

## 1. What Changed vs Day 11

| Feature | Day 11 | Day 12 |
|---|---|---|
| Startup time (2nd run) | 8 minutes (re-embeds everything) | Instant (loads from cache) |
| Source of each chunk | Unknown | Tracked — shows which `.md` file |
| Wrong answer debugging | Impossible | Print retrieved chunks + scores |
| Bad retrieval from noise files | Polluted results | Excluded via `SKIP_FILES` |
| Over-represented files | One file could dominate all 5 slots | Max 2 chunks per file (deduplication) |
| Score threshold | No floor | Refuses to answer if best score < 0.4 |

---

## 2. Persistent Embeddings — How It Works

### The problem

Day 11 re-embedded all 467 chunks every run. 8 minutes of waiting before you could ask a single question.

### The solution

Save embeddings to `embeddings.json` after the first run. Load from file on all subsequent runs.

```python
CACHE_FILE = "./embeddings.json"

if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        embeddings = json.load(f)
    print(f"Loaded {len(embeddings)} embeddings from cache.")
else:
    # embed all chunks...
    with open(CACHE_FILE, "w") as f:
        json.dump(embeddings, f)
    print("Embeddings saved to cache.")
```

**First run:** embeds 467 chunks (~8 minutes), saves `embeddings.json`  
**Every run after:** loads in < 1 second

### The cache structure

Each entry in `embeddings.json`:
```json
{
  "Cosine similarity measures the angle between two vectors...": {
    "source": "day-03-corrections-and-gaps.md",
    "vector": [0.037, -0.022, 0.011, ...]
  }
}
```

The key is the chunk text, the value contains the source filename and the 384-dimensional vector.

### When to rebuild the cache

Delete `embeddings.json` and re-run when:
- You add new day files to `days/`
- You change the chunk filter threshold
- You switch embedding models

```powershell
Remove-Item embeddings.json
python rag_v2.py  # rebuilds automatically
```

---

## 3. Source Tracking — Seeing Where Answers Come From

Every chunk now stores its source file. The query loop prints retrieved chunks with scores AND sources:

```
Retrieved chunks:
  [0.724] (day-03-corrections-and-gaps.md) **Cosine similarity** measures the angle...
  [0.719] (day-03-corrections-and-gaps.md) **Cosine similarity:** Measures the angle...
  [0.656] (day-07-pipeline-hands-on.md) **Cosine similarity (proved):** The similarity...
Sources: day-03-corrections-and-gaps.md, day-07-pipeline-hands-on.md
```

This turns retrieval from a black box into an inspectable step. When the answer is wrong, you immediately see which chunks were retrieved and why.

---

## 4. Retrieval Debugging in Action — The Temperature Problem

### The failure (Day 11)

Query: `what temperature should I use for coding?`  
Answer: `0.1°C` — wrong, confused AI temperature with physical temperature.

### Debugging with source tracking

After adding source tracking:
```
Retrieved chunks:
  [0.775] (day-11-rag-over-notes.md) You: what temperature should I use for coding?
  [0.585] (day-11-rag-over-notes.md) The query was "what temperature should I use for coding?"...
```

**Diagnosis:** Day 11's notes documented the failure, so those chunks scored highest. The actual temperature guide from Day 02 scored only 0.478 and ranked 3rd.

### Fix 1 — Exclude meta-documentation files

```python
SKIP_FILES = {"day-11-rag-over-notes.md", "day-12-rag-improved.md"}
```

Files that document failures and process notes contaminate the knowledge base. They get excluded from the corpus.

### Fix 2 — Source deduplication

Prevents one file from dominating all top slots:

```python
seen_sources = {}
deduped = []
for text, source, score in result:
    if source not in seen_sources:
        seen_sources[source] = 0
    if seen_sources[source] < 2:  # max 2 chunks per file
        deduped.append((text, source, score))
        seen_sources[source] += 1
    if len(deduped) == 5:
        break
```

After fix: Day 02's temperature guide ranked 1st and 2nd with clean scores.

### Fix 3 — Score threshold

If the best chunk scores below 0.4, don't answer at all:

```python
if result[0][2] < 0.4:
    print("\nAI: I don't have relevant information about that in my notes.")
    continue
```

This prevents the model from hallucinating an answer when retrieval finds nothing relevant.

---

## 5. The Key Lesson — Retrieval vs Generation Quality

After all fixes, the temperature answer improved but was still slightly off — the model confused probability percentages in the retrieved table with temperature values.

This revealed an important distinction:

| Problem type | Cause | Fix |
|---|---|---|
| **Retrieval failure** | Wrong chunks retrieved | Better chunking, deduplication, exclusions |
| **Generation failure** | Right chunks retrieved, wrong answer synthesized | Bigger/better generation model |

After fixes, the right chunks ARE retrieved (Day 02 temperature guide in top 2). The wrong synthesis is a **phi3:mini limitation** — it's a small model that gets confused by numeric tables.

The same retrieved chunks sent to GPT-4 or Claude would produce the correct answer: "Use 0.1–0.3 for coding tasks."

**This is the most important engineering insight of RAG:** debug retrieval and generation separately. Most "bad RAG" problems are retrieval problems, not generation problems.

---

## 6. Final Results After All Improvements

```
You: what is cosine similarity?

Retrieved chunks:
  [0.724] (day-03-corrections-and-gaps.md) Cosine similarity measures the angle...
  [0.719] (day-03-corrections-and-gaps.md) Cosine similarity: Measures the angle...
  [0.656] (day-07-pipeline-hands-on.md) Cosine similarity (proved): cat/kitten (0.79)...

AI: Cosine Similarity measures the angle between two vectors, indicating their
    directional similarity regardless of vector length. If they point in roughly
    the same direction, they are considered similar in meaning — cat/kitten (0.79)
    > cat/dog (0.66) > cat/car (0.46).  ✅
```

---

## Key Takeaways

**Persistent cache is not optional for real use.** Re-embedding 467 chunks every run is 8 minutes of waste. Save once, load forever. Delete only when the corpus changes.

**Source tracking turns retrieval into a debuggable step.** Without it, you're guessing why the answer is wrong. With it, you see exactly which chunks were retrieved and from which file.

**Bad RAG answer = bad retrieval OR bad generation — debug them separately.** Print the retrieved chunks first. If they're wrong, fix retrieval. If they're right, the problem is the generation model.

**Meta-documentation contaminates your knowledge base.** Notes that document failures score highly for the same queries as the failures they document. Exclude them explicitly.

**Deduplication prevents one file from dominating.** Without it, the best-matching file fills all 5 slots. Cap chunks per file to force diversity.

**Score threshold prevents hallucination.** When nothing relevant is retrieved, the model will make something up. Refuse to answer below a minimum score.

---

## One-Line Summaries

**Persistent cache:** Embed once → save to JSON → load in 1 second forever. Delete when corpus changes.

**Source tracking:** Store `{chunk: {source, vector}}` instead of `{chunk: vector}` — tells you which file every answer came from.

**Retrieval vs generation:** Right chunks + wrong answer = generation model problem. Wrong chunks + wrong answer = retrieval problem. Always debug retrieval first.

**Score threshold:** If best match < 0.4, say "I don't know" — prevents confident wrong answers from irrelevant context.

**Deduplication:** Cap chunks per source file to force diverse retrieval across your knowledge base.

---

## Revision Questions

1. **You run `rag_v2.py` for the first time. What happens? You run it again immediately. What happens differently?**
2. **When should you delete `embeddings.json` and rebuild?**
3. **The cache structure changed from Day 11. What does each entry now store and why?**
4. **A query gives a wrong answer. You print the retrieved chunks. Top result is from `day-11-rag-over-notes.md` with score 0.775. What is the problem and how do you fix it?**
5. **What does source deduplication do? Why is it needed?**
6. **Best retrieved chunk scores 0.22. What does the system do and why?**
7. **Retrieved chunks are correct but the answer is still wrong. Is this a retrieval problem or generation problem? What's the fix?**
8. **You add Day 13 notes to `days/`. Do you need to rebuild the cache? What exact steps?**
9. **Why are `day-11-rag-over-notes.md` and `day-12-rag-improved.md` excluded from the corpus?**
10. **Your `embeddings.json` is 50MB. A colleague asks "why is this file so large?" Explain what's in it.**
