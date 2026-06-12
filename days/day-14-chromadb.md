# Day 14 — ChromaDB (Replacing JSON Cache with a Real Vector Database)

> Previous: [Day 13 — Structured JSON Output](day-13-structured-output.md)

## What This Day Is About

Replaced the manual `embeddings.json` file + cosine similarity loop with **ChromaDB** — a proper vector database that runs locally, persists data to disk, and handles similarity search internally. Same RAG logic, same results, but now using production-grade infrastructure instead of a hand-rolled solution.

---

## 1. The Result

**First run:** Embeds 498 chunks, stores in `chroma_db/` folder (~8 minutes)
```
Populating chromaDB...
Embedding chunk 0/498...
...
Added 498 chunks to chromaDB.
```

**Every run after:** Loads instantly from disk
```
Loaded 498 chunks from chromaDB.
```

**Query results:**
```
You: what is cosine similarity?

Retrieved chunks:
  [dist=0.259] (day-03-corrections-and-gaps.md) **Cosine similarity** measures the angle...
  [dist=0.315] (day-03-corrections-and-gaps.md) **Cosine similarity:** Measures the angle...
  [dist=0.385] (day-03-corrections-and-gaps.md) Cosine similarity cares about direction...

Answer: Measures the angle between two vectors, indicating their directional similarity regardless of vector length.
Confidence: high
```

---

## 2. What Changed vs Day 12

### Before (manual approach)
```python
# Load all vectors into RAM as a Python dict
embeddings = json.load(open("embeddings.json"))

# Loop ALL 467 chunks computing cosine similarity manually
for text, data in embeddings.items():
    score = cosine_similarity(query_vector, data["vector"])
    result.append((text, data["source"], score))

result.sort(...)  # manual sort
result = deduped[:]  # manual deduplication
```

### After (ChromaDB)
```python
# ChromaDB handles search — one call
results = collection.query(
    query_embeddings=[query_vector],
    n_results=5,
    include=["documents", "metadatas", "distances"]
)
```

**Lines of code removed:** ~20 lines of manual cosine loop, sort, deduplication  
**Lines of code added:** 6 lines of ChromaDB query

---

## 3. ChromaDB Core Concepts

### PersistentClient — the database
```python
client = chromadb.PersistentClient(path="./chroma_db")
```
Creates (or opens) a database stored in the `./chroma_db` folder. Works like SQLite — a folder on disk, no separate server process needed.

### Collection — the table
```python
collection = client.get_or_create_collection(name="ai_notes")
```
A collection is like a table in a relational database. It stores documents, their embeddings, and any metadata. `get_or_create_collection` opens it if it exists or creates it if not.

### Adding documents
```python
collection.add(
    documents=texts,          # list of chunk text strings
    embeddings=vectors,       # list of 384-dim vectors
    metadatas=metadatas,      # list of {"source": "filename"} dicts
    ids=ids                   # list of unique string IDs
)
```
Called once when the collection is empty. After this, data is persisted to disk.

### Querying
```python
results = collection.query(
    query_embeddings=[query_vector],   # your embedded question
    n_results=5,                       # how many results to return
    include=["documents", "metadatas", "distances"]
)
```
Returns the top-N most similar chunks. ChromaDB uses **HNSW** (Hierarchical Navigable Small World) — an approximate nearest neighbor algorithm that finds similar vectors without checking every single one.

### Reading results
```python
texts     = results["documents"][0]    # list of matching chunk texts
metas     = results["metadatas"][0]    # list of {"source": "filename"}
distances = results["distances"][0]    # list of distances (lower = more similar)
```
Note the `[0]` — ChromaDB supports batch queries, so results are nested one level deep.

---

## 4. Distances vs Scores

In Days 09–13, similarity was a **score** (higher = more similar, 0.0–1.0).  
In ChromaDB, similarity is a **distance** (lower = more similar).

| Meaning | Manual cosine (Days 09–13) | ChromaDB |
|---|---|---|
| Very similar | score = 0.87 | distance = 0.13 |
| Related | score = 0.65 | distance = 0.35 |
| Unrelated | score = 0.20 | distance = 0.80 |

The threshold check flips accordingly:
```python
# Old: refuse if best score too low
if result[0][2] < 0.4:

# New: refuse if best distance too high
if distances[0] > 0.6:
```

---

## 5. Why ChromaDB Beats a JSON File

| Aspect | JSON file (Days 12–13) | ChromaDB (Day 14) |
|---|---|---|
| **Storage** | One flat file, all in RAM | Folder on disk, indexed |
| **Search** | Loop all N vectors manually | HNSW index, sub-linear time |
| **Scale** | Breaks at millions of docs (RAM) | Handles millions efficiently |
| **Startup** | Load entire file into RAM | Open DB, ready to query |
| **Updates** | Re-embed everything | `collection.add()` new docs only |
| **Code** | ~20 lines of search logic | 6 lines |
| **Deduplication** | Manual | Can use `where` filters |

### The math at scale

```
467 docs × 384 dimensions × 4 bytes = ~720 KB  ← fits in RAM fine
1M docs  × 384 dimensions × 4 bytes = ~1.5 GB  ← JSON approach breaks
10M docs × 384 dimensions × 4 bytes = ~15 GB   ← impossible without DB
```

ChromaDB with HNSW finds the top-5 results from 10M docs in milliseconds. The JSON loop would take minutes.

---

## 6. How to Reset the Database

If you add new day files and need to re-index:
```powershell
Remove-Item -Recurse chroma_db
python rag_chroma.py   # rebuilds automatically
```

Or selectively add new documents:
```python
collection.add(documents=[new_text], embeddings=[new_vector], 
               metadatas=[{"source": "day-15.md"}], ids=["498"])
```

---

## 7. What ChromaDB Stores on Disk

```
chroma_db/
├── chroma.sqlite3          ← metadata, collection info
└── [uuid]/
    ├── data_level0.bin     ← HNSW index (the actual vectors)
    ├── header.bin
    └── length.bin
```

The `.sqlite3` file stores collection metadata and document text. The binary files are the HNSW index — a specialized data structure for fast approximate nearest neighbor search.

---

## Key Takeaways

**ChromaDB replaces the JSON file with a real indexed database.** Same data, same embeddings, but now stored in a structure optimized for similarity search.

**`collection.query()` replaces the entire manual cosine loop.** 20 lines of search logic becomes 6 lines of ChromaDB API.

**Persistence is built in.** `PersistentClient` saves to disk automatically. No manual `json.dump()` needed.

**HNSW scales to millions.** The JSON loop is O(N) — every query scans all docs. HNSW is approximately O(log N) — fast even at massive scale.

**Distances not scores.** ChromaDB returns distances (lower = better). Adjust threshold checks accordingly.

---

## One-Line Summaries

**PersistentClient:** Opens or creates a ChromaDB database stored as a folder on disk — like SQLite for vectors.

**Collection:** A named table in ChromaDB that stores documents, their vectors, and metadata.

**collection.query():** One call that replaces the entire manual cosine similarity loop — ChromaDB's HNSW index finds the top-N results.

**HNSW:** Approximate nearest neighbor algorithm — finds similar vectors in O(log N) instead of O(N), enabling vector search at millions of documents.

**Distance vs score:** ChromaDB returns distances (lower = more similar), opposite of cosine similarity scores (higher = more similar).

---

## Revision Questions

1. **What does `PersistentClient(path="./chroma_db")` do? What gets stored in that folder?**
2. **You call `get_or_create_collection("ai_notes")`. What happens if the collection already exists? What if it doesn't?**
3. **Why does `collection.count() == 0` check work for detecting a fresh database?**
4. **ChromaDB returns `distances[0] = 0.26` for the top result. Is this a good match or a bad match?**
5. **Your old code checks `if score < 0.4: refuse`. How does this check look in ChromaDB?**
6. **Why does `results["documents"][0]` have a `[0]` index? What would `results["documents"][1]` be?**
7. **You have 10 million documents. Compare query time: manual JSON loop vs ChromaDB HNSW. Why is ChromaDB faster?**
8. **You add 50 new day files to your notes. Do you need to rebuild the entire database? What's the alternative?**
9. **What files are inside the `chroma_db/` folder and what does each store?**
10. **Name 3 things ChromaDB gives you that the `embeddings.json` approach doesn't.**
