# Question Bank

Used by the daily revision block (see `AGENTS.md`, "Instructor & Evaluator Role"). Claude adds a few questions per day from the `days/` notes. Format: `[MCQ|FREE] question` then the answer key. Track when each was last asked in `scorecard.md`.

## Day 40 - Switching the embedding provider

- [FREE] Why must chunks and the user's question be embedded by the same model?
  - Answer: vectors only compare meaningfully within one embedding space; different models give different dimensions and meanings.
- [MCQ] `gemini-embedding-001` output_dimensionality=768 means: (a) paragraphs are limited to 768 words (b) each text becomes a vector of 768 numbers (c) at most 768 chunks per batch (d) 768 tokens max input.
  - Answer: (b). Input limit is 2,048 tokens.
- [FREE] What does `task_type` do, and which value goes on stored chunks vs the user's question?
  - Answer: a label for how the vector will be used; RETRIEVAL_DOCUMENT for chunks, RETRIEVAL_QUERY for the question.
- [FREE] Why is rebuilding the index at app startup a bad idea with a 100-texts/minute limit?
  - Answer: ~800 chunks need 8+ minutes, so startup stalls on Render; build once offline and ship the vectors.

## Days 1-39

(To be added from the day notes as revision proceeds.)
