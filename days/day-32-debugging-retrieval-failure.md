# Day 32 — Debugging A Real RAG Retrieval Failure

**Goal:** Investigate why the Day 31 eval harness's one failing question (Q7: "why did the embedding step break when deployed") got a wrong, hallucinated answer, despite the correct explanation existing word-for-word in Day 28's own note.

---

## The Investigation

1. Called `retrieve_chunks()` directly with the failing question and printed the top 5 results with distances/sources — **none were from `day-28-removing-ollama-dependency.md`**, the note that actually explains the real cause.
2. Fetched every chunk from that file directly (`collection.get(where={"source": ...})`) to confirm the correct explanation exists as a chunk. It does — chunk 1: *"Ollama isn't a cloud API... a deployed server is a different machine, so it can never reach `localhost:11434`..."* — a clear, correct answer.
3. Widened the search to `n_results=20` to find where Day 28's chunks actually ranked. Found 3 Day 28 chunks at ranks #9, #14, #20 — but **none of them were chunk 1**, the actually-useful explanation. It didn't appear even in the top 20.

## The Real Cause: Chunking Split The Answer Across Two Chunks

Chunk 0 says: *"the embedding call depended on local Ollama... which only exists on my own machine."* — contains the word **"embedding."**
Chunk 1 says: *"Ollama isn't a cloud API... deployed server is a different machine..."* — contains the actual **"why,"** but never uses the word "embedding" at all.

The question asked "why did the **embedding** step break" — but the one chunk with the complete, correct "why" doesn't contain that specific word, because paragraph-based chunking split one coherent explanation into two adjacent paragraphs, each carrying only part of the necessary vocabulary. Individually, neither chunk is a strong enough semantic match to rank in the top 10-20, even though together they'd answer the question perfectly.

## What Was Fixed vs. What Wasn't

- **Fixed:** `retrieve_chunks()`'s default `n_results` was `5`, too narrow for a 697-chunk corpus — bumped to `10`. This helps *other* borderline questions where the right chunk was just outside the cutoff.
- **Not fixed (deliberately):** This specific chunking-split issue. A real fix would mean changing the chunking strategy itself (e.g. merging short adjacent paragraphs, or adding chunk overlap so context isn't lost at paragraph boundaries) — a bigger structural change not worth making for one edge-case question.

## Key Learning

A RAG system's retrieval quality depends as much on **how documents were split into chunks** as on the embedding model or the number of results requested. A single well-written explanation split across two paragraph-chunks can become *individually* unmemorable to a similarity search, even when the original prose reads perfectly to a human. This is the exact same chunking-strategy lesson from Day 11/12, resurfacing in a new, real place — evals don't just catch bugs, they reveal genuine architectural limits.

## File Updated

- `projects/day-27/awesome-project/assistant.py` (`retrieve_chunks` default `n_results`: 5 → 10)

## Next Step

Redeploy to Render, re-run `run_eval.py` against the live URL, and confirm the overall pass rate — accepting that this one specific question may still not reach a perfect answer, and that's an honest, documented limitation rather than a bug to chase further right now.

## Result After Deploying The Fix

Re-ran the full eval suite against the live URL. **Q7 now passes** — and correctly explains both the Ollama local-only cause *and* references the chunking-split issue, because this very note (`day-32-debugging-retrieval-failure.md`) got retrieved as source material once it was live. The bug and its own documentation became part of the fix.

Pass rate stayed at **9/10 (90%)**, but the specific failure shifted: **Q1 ("what is temperature") now fails** — not a real regression, the answer is still substantively correct (*"adjusts the softness of the model's probability distribution"*), it just no longer contains the literal word "logits" that the eval strictly requires, because `n_results=10` changed which chunks got summarized, which changed the generated phrasing. This is a **false negative from an overly strict single-keyword check**, not an actual answer-quality problem — a limitation of the eval design itself, worth revisiting (e.g. accept multiple valid keywords per question) rather than the RAG system.

