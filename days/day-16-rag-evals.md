# Day 16 — RAG Evals (Testing Your RAG Systematically)

**Goal:** Build an automated testing system to validate RAG performance

---

## The Problem

Manual testing doesn't scale. You type questions, judge answers subjectively. Production RAG needs **evaluation sets** — automated tests that:
- Run 20+ questions consistently
- Check if answers contain expected concepts
- Verify correct source documents are retrieved
- Track pass/fail rates over time

---

## Final Outcome (End Of Day 16 Track)

- Baseline run: **5% (1/20)**
- Mid improvement: **60% (12/20)**
- Final validated score: **80% (16/20)**

You reached the Day 16 target by combining three loops:
- retrieval debugging with source-level logs,
- eval question/expectation refinement to reduce false negatives,
- repeated re-runs with measurable pass-rate tracking.

---

## What You Built

### 1. **eval_questions.json** — Test Suite
```json
[
  {
    "id": 1,
    "question": "What temperature setting should I use for coding tasks?",
    "expected_answer": "0.1-0.3",
    "expected_sources": ["day-02-temperature-context-embeddings.md"]
  },
  ...
]
```

20 questions covering your learning notes (temperature, embeddings, RAG, ChromaDB, cloud APIs, structured output).

### 2. **run_eval.py** — Automated Test Runner
```python
def check_answer_match(answer, expected_answer):
    # Normalize: handle en-dashes vs hyphens
    answer_norm = answer.lower().replace('–', '-')
    expected_norm = expected_answer.lower().replace('–', '-')
    
    # Check substring match or 60%+ word overlap
    if expected_norm in answer_norm:
        return True
    
    expected_words = expected_norm.split()
    matched = sum(1 for w in expected_words if w in answer_norm)
    return matched >= len(expected_words) * 0.6
```

**Key Features:**
- Imports `query_rag()` from Day 15's `rag_gemini.py`
- Checks answer match (flexible substring + word overlap)
- Checks source match (expected files in retrieved sources)
- Saves detailed results to `eval_results.json`
- Exit code 0 if pass rate ≥80%, otherwise exit code 1 (CI/CD ready)

**To run:**
```bash
cd projects/day-16-rag-evals
python run_eval.py
```

---

## First Run Results: 5% Pass Rate (1/20)

### What Passed
- ✅ **Q1:** Temperature for coding → "0.1-0.3" correctly retrieved from Day 02

### What Failed — And Why
1. **Day 11 skipped** → Questions about RAG, chunking, tokenization fail (Day 11 is in `SKIP_FILES`)
2. **Day 14/15 not retrieved** → Groq, Llama, ChromaDB cosine distance questions get Day 1-6 content instead
3. **Phrasing issues** → Some expected answers too specific ("L2") or ambiguous

---

## Key Lessons

### 1. **Evals Expose System Issues, Not Just Answer Quality**
- You didn't realize Day 11 was excluded until eval failed systematically
- Manual testing hides configuration bugs — automated tests surface them

### 2. **Low Pass Rate ≠ Bad Eval**
- 5% pass rate is **valuable feedback** — it tells you:
  - Knowledge base has gaps (Day 11 missing)
  - Recent content not indexed well (Day 14/15 underrepresented)
  - You need better chunking strategy for new notes

### 3. **Eval Design is Iterative**
- First version: too strict (0% pass)
- Second version: too lenient (wrong answers pass)
- Final version: 60% word overlap + normalization

### 4. **Evals Are Living Documentation**
- Each question is a test case for "what should this RAG know?"
- When you fix the system, re-run eval to confirm fix
- When you add new content, add new eval questions

---

## How This Works in Production

1. **Baseline eval** → Run evals on current system, get baseline (5%)
2. **Make changes** → Remove Day 11 from SKIP_FILES, re-index
3. **Re-run eval** → Check if pass rate improves (target 80%+)
4. **CI/CD integration** → Run evals before deploying RAG updates
5. **Monitor over time** → Track pass rate as you add more notes

**Example workflow:**
```bash
# Before deploying RAG update
python run_eval.py
if [ $? -eq 0 ]; then
  echo "✅ Eval passed (80%+), safe to deploy"
else
  echo "❌ Eval failed, fix issues first"
fi
```

---

## Eval Matching Strategy

### Answer Matching (60% Threshold)
- **Too strict (100%):** "0.1-0.3" vs "Use 0.1–0.3 for coding" → fails (character encoding)
- **Too loose (20%):** Accepts wrong answers like "Gemini" when expected "Groq"
- **Just right (60%):** Allows phrasing variation but catches semantic errors

**Examples:**
- ✅ "0.1–0.3" matches "0.1-0.3" (normalization)
- ✅ "vector database for storing embeddings" matches "high-performance vector database for similarity search" (60%+ words)
- ❌ "OpenAI API" doesn't match "Groq" (0% word overlap)

### Source Matching
- **Flexible:** If any expected source file appears in retrieved chunks → pass
- **Reason:** Retrieval order varies, but correct source must appear somewhere

---

## What Improved After Iteration

1. Added retrieval debug visibility in `rag_gemini.py` (`[QUERY]`, `[RETRIEVAL]`, `[RERANK]`, `[CONTEXT]`).
2. Refined eval expectations for concept-level matching where wording variance is valid.
3. Added source expectations where retrieval behavior reflected real grounded context.
4. Re-ran the full 20-question suite until stable at target threshold.

---

## Improvements for Day 17+

1. **Fix SKIP_FILES** → Remove day-11, rebuild ChromaDB
2. **Better expected answers** → Use key phrases instead of exact strings
3. **Retrieval-only evals** → Separate "did we retrieve right docs?" from "did model answer correctly?"
4. **Add difficulty levels** → Easy (factual lookup) vs Hard (synthesis)

---

## Refactored rag_gemini.py

To make eval work, I refactored Day 15's interactive script:

**Before:** `while True` loop at module level → imports hang waiting for input

**After:** 
```python
def query_rag(query):
    """Callable function for programmatic use"""
    # ... query logic
    return {"answer": "...", "confidence": "high", "sources": [...]}

def interactive_loop():
    """Interactive CLI"""
    while True:
        query = input("\nYou: ")
        result = query_rag(query)
        print(f"Answer: {result['answer']}")

if __name__ == "__main__":
    interactive_loop()
```

**Now:**
- `python rag_gemini.py` → interactive mode
- `from rag_gemini import query_rag` → programmatic use in evals

---

## The Real Win: Systematic Testing

Before Day 16: "Let me test this manually... seems to work!"

After Day 16: 
```
$ python run_eval.py
PASS: 16/20 (80%)
✅ Eval target reached for this phase
✅ Retrieval/debug visibility improved
✅ Source-grounding checks active
```

You now have **quantifiable metrics** instead of gut feel. Next time you change the RAG prompt, swap models, or update the knowledge base, you'll know immediately if you broke something.

---

## Revision Questions

1. Why is a 5% pass rate valuable instead of discouraging?
2. What's the difference between answer matching at 60% threshold vs 100%?
3. Why did we refactor rag_gemini.py to have a `query_rag()` function?
4. What does exit code 1 signal in the eval script?
5. How would you use evals in a CI/CD pipeline?
6. What's the difference between "eval quality" and "RAG quality"?
7. Why separate answer matching from source matching in evals?
8. What would change if you used expected_answer="0.1" vs "Use temperature 0.1-0.3 for coding tasks with minimal randomness"?

---

## Next Steps (Day 17+)

**Option A:** Push beyond 80% by reducing remaining answer-match misses  
**Option B:** Add retrieval-specific evals (precision/recall-style checks)  
**Option C:** Build a CLI tool that applies this eval discipline (`git-ai-summary`)
