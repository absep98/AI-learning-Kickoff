# Learning Scorecard

Maintained by Claude (instructor/evaluator). Scoring: 0 = wrong/blank, 1 = partial or shaky, 2 = correct and clear.
Rules live in `AGENTS.md` under "Instructor & Evaluator Role".

## Revision list (topics scoring below 2, oldest first)

- Same-model rule for embeddings: the same-dimension, different-model case (silent wrong answers) was missed (2026-10-27).
- Day 37 cache poisoning: why mutating a returned dict corrupts the cache; `dict(b)` copies (shallow) (2026-10-28).
- Eval design: judge whether the answer is truly correct before editing the keyword; loosening criteria risks passing wrong answers (2026-10-28).
- Relevance threshold is tied to one embedding model's distance scale; re-measure after switching models (2026-10-27).

## Eval log

| Date | Type (daily/weekly) | Topics | Scores | Gaps found | Next action |
| --- | --- | --- | --- | --- | --- |
| 2026-10-14 | setup | n/a | n/a | Baseline eval not yet run | Run first weekly eval |
| 2026-10-27 | daily (partial, 2 of 5 asked) | Day 40: same-model rule, threshold root cause | 1/2, 1/2 | Only named the loud dimension-mismatch case, missed the silent same-dimension failure. Said the threshold was lowered but not why a model switch invalidates it (threshold is model-specific) | Ask both again next session, then Q3-Q5 of the block (older-day MCQ + free, "what breaks") |
| 2026-10-28 | daily (Day 40 block, cont.) | Day 37 cache mutation (MCQ), Python reference vs copy | 1/2, 1/2 | MCQ right but could not explain why; reference half of `a = b` correct, did not say what `a = dict(b)` does (new independent dict, shallow copy) | Re-ask both next session; Q5 (what breaks / why this design) still owed |
| 2026-10-28 | daily (Day 41 block) | Day 41 eval re-run: app bug vs eval bug | 1/2 | Saw the keyword was too narrow and proposed more keywords, but did not first verify the answer was correct or name the risk of loosening criteria (passing wrong answers; Day 32 lesson) | Re-ask next session; Day 40 Q1-Q2 and Day 37/Python-reference rows still open |

