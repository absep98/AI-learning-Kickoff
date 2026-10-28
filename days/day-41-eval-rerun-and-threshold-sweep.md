# Day 41 - Re-running the Live Eval and Sweeping the Threshold

**Status: done.** The live eval ran at 12/13, the threshold was checked against 24 labelled questions, and a real gap was found: two out-of-scope questions still get fake-sourced answers.

## Why

Day 40 switched embeddings to Gemini and moved `DISTANCE_THRESHOLD` from 0.75 to 0.35 on a hand-picked set of 10 questions. Today's goal was to check that on the deployed app, and to test the number properly instead of trusting a gut call.

## What I did

1. **Re-ran the Day 31 eval against the live site.** Found two problems with the tool first, before trusting the number:
   - The Day 38 rate limit (5 requests per 60 s, blocked when `len(recent) >= 5`) would block the last requests of a 10-question burst; the eval reads `data.get("message", "unknown")`, so blocked requests would count as failures. Fix: `time.sleep(15)` in a `finally:` so it runs on success and on error.
   - The eval had no "should refuse" questions, so it could not have caught Day 40's bug. Added 3 (World Cup, cooking rice, capital of the USA).
2. **Result: 12/13 (92.3%).** All 3 refuse cases passed. The one failure (Q1 "what is temperature", keyword `logits`) was a keyword that was too narrow, not an app bug: the answer was correct.
3. **Threshold sweep** (`projects/day-41-threshold-sweep/sweep.py`): 24 questions labelled by what *should* happen (15 answer, 9 refuse), the best distance collected once, then 5 thresholds counted for false refusals and false answers.

| Threshold | False refusals | False answers | Total |
|---|---|---|---|
| 0.25 | 10 | 1 | 11 |
| 0.30 | 5 | 1 | 6 |
| **0.35** | **0** | **2** | **2** |
| 0.40 | 0 | 5 | 5 |
| 0.45 | 0 | 6 | 6 |

0.35 stays: fewest total mistakes on a bigger set, so the Day 40 choice was not just lucky.

## What I learned

- **Distance measures topical similarity, not whether a chunk can answer the question.** "How does LoRA fine-tuning work" scores as close to my notes as "what is temperature", because the notes cover model training, even though LoRA is never mentioned. No threshold can separate "covered" from "adjacent topic". (It is semantic closeness, not keyword overlap.)
- **The prompt "answer only using the provided context" does not hold.** Live, LoRA got a fluent answer from the model's own knowledge and "GPT-4's context window is 8000 tokens" was stitched from a generic "8K context window" example, both with note files cited as sources. The same fake-provenance failure as the Day 40 World Cup bug, in a milder form.
- **Label questions by what should happen, before looking at distances.** My own label for "train from scratch" was wrong (the notes do cover it); fixing the label, not the threshold, gave an honest sweep.
- **A tool that measures can be broken without the app being broken.** The rate limit would have turned a healthy app into a failing eval.
- **Loosening an eval criterion** (more keywords for Q1) needs the answer checked as correct first, and risks passing wrong answers later.
- **Which mistake is worse is a design decision:** a false answer (confident, grounded-looking, wrong) costs more than a false refusal for a notes assistant.

## Real mistakes made

1. Edited the Day 16 eval instead of the Day 31 live eval.
2. `time.sleep` placed outside the `try` block (SyntaxError); it belongs in `finally`.
3. Predicted 4 of 10 requests would pass a limit of `>= 5` (5 pass).
4. Wrote the sweep's refusal condition backwards (a refusal of a should-refuse question is correct), used a boolean flag instead of a counter, used `else` where a specific condition was needed, and printed inside the inner loop.
5. Added a corrected question as a new line instead of editing the old one, leaving a conflicting duplicate label.
6. Explained near-miss closeness as "word overlap" instead of topical similarity.

All of these are logged in `evals/mistakes-log.md`.

## Where we left off (Day 42 start)

1. **Fix the grounding gap.** Two questions still produce answers that are not supported by the retrieved chunks. The retrieval threshold can't catch them and the prompt instruction is ignored. Option to learn: a post-answer check (an LLM judge or a "not in notes" signal) that compares the answer to the retrieved chunks. Unanswered: what should that check compare?
2. Widen Q1's expected keywords in the Day 31 eval carefully (verify the answer first, add alternatives deliberately).
3. Add the sweep's near-miss questions (LoRA, GPT-4 context) to the live eval as "should refuse" cases so the gap shows up as a failing test.
4. Re-ask the open rows in `evals/mistakes-log.md`; two revision blocks in a row scored 1 on explaining *why*.
