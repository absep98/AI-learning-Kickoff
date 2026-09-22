# Day 24 — Repo Assistant: RAG + Tool Routing

**DRAFT — written retroactively from actual commits/tests, review and personalize before treating as final.**

**Goal:** Ship a real feature by combining two previously separate prototypes — Day 14's RAG retrieval and Day 18-23's tool-calling loop — into one working assistant, matching the "Agentic RAG" / "RAG SQL Router" pattern (validated against `patchy631/ai-engineering-hub` as the right difficulty level).

---

## What Was Built

- New project: `projects/day-24-repo-assistant/repo_assistant.py`.
- `retrieve_chunks(query, n_results=5)` — extracted retrieval logic out of `rag_chroma.py`'s monolithic script (which mixed retrieval and generation inline) into its own reusable function: embed query → `collection.query()` → return `(texts, metas, distances)`.
- `answer_question(query)` — takes retrieved chunks, checks the distance threshold, calls Groq (`openai/gpt-oss-20b`) to generate a grounded, cited answer.
- `check_git_status()` — runs `git status --short` against the repo and summarizes changed file count.
- `plan_action(query)` — rule-based keyword router deciding between `answer_question` and `check_git_status`.
- A `while True` loop in `__main__` with quit handling, same pattern as `mock_loop.py`.

## Test Evidence

- `"what is temperature"` → routed to `answer_question`, returned a real cited answer from `day-02`, `day-05`, `day-11` notes.
- `"check git status"` → routed to `check_git_status`, returned `"Git status: 5 changed file(s)"`.
- Sequential run (`what is temperature` → `check git status` → `quit`) confirmed the loop handles multiple turns and exits cleanly.

## File Created

- `projects/day-24-repo-assistant/repo_assistant.py`

## Key Learning

Retrieval and generation should be separate functions, not one inline block — `rag_chroma.py` never separated them, which made it impossible to reuse just the retrieval half. Splitting it out here made everything after (routing, testing, deployment) much easier.

## Next Step

Replace `plan_action`'s keyword matching with a model-based planner, so routing survives typos/rephrasing instead of relying on literal keyword luck.
