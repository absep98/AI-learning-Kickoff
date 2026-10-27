# Learning Scorecard

Maintained by Claude (instructor/evaluator). Scoring: 0 = wrong/blank, 1 = partial or shaky, 2 = correct and clear.
Rules live in `AGENTS.md` under "Instructor & Evaluator Role".

## Revision list (topics scoring below 2, oldest first)

- Same-model rule for embeddings: the same-dimension, different-model case (silent wrong answers) was missed (2026-10-27).
- Relevance threshold is tied to one embedding model's distance scale; re-measure after switching models (2026-10-27).

## Eval log

| Date | Type (daily/weekly) | Topics | Scores | Gaps found | Next action |
| --- | --- | --- | --- | --- | --- |
| 2026-10-14 | setup | n/a | n/a | Baseline eval not yet run | Run first weekly eval |
| 2026-10-27 | daily (partial, 2 of 5 asked) | Day 40: same-model rule, threshold root cause | 1/2, 1/2 | Only named the loud dimension-mismatch case, missed the silent same-dimension failure. Said the threshold was lowered but not why a model switch invalidates it (threshold is model-specific) | Ask both again next session, then Q3-Q5 of the block (older-day MCQ + free, "what breaks") |
