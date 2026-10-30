# Day 42 - A Grounding Check: Don't Trust The Prompt, Verify In Code

**Status: built and verified locally; pushed to deploy.** Out-of-scope questions that slip past the distance threshold are now refused instead of answered from the model's memory with fake note sources.

## Why

Day 41's threshold sweep showed that distance measures topical similarity, not whether a chunk can answer the question. LoRA and "GPT-4 context window" passed the 0.35 gate and got answers from the model's own training, with note files cited as sources, even though the system prompt says "answer only using the context". A prompt is a request, not a guarantee.

## The design

1. The model must return JSON with two fields: `answer` and `quote` (one sentence copied exactly from the retrieved context). It returns empty strings when the context lacks the answer.
2. Code checks the quote: `quote_in_context(quote, context)`. A missing or empty quote, or a quote not found in the chunks, means refuse ("No relevant notes found").
3. Fail closed: invalid JSON, wrong types, a missing field, an empty answer or a failed quote check all refuse. The quote is used only for the check and is never shown to the user.

## Concepts learned

- **Provenance** = where a piece of information came from. The bug was wrong provenance: an answer from model memory labelled with note files as the source.
- **Verify outside the model.** Code can't be persuaded; a prompt instruction can be ignored. Checks that matter belong in plain code.
- **What the quote check proves and doesn't.** It proves the quote exists in the retrieved text, not that it supports the answer. A real but irrelevant quote passes (seen live: the model answered "I don't have information on LoRA" with an unrelated real quote). Possible next layer: word overlap or embedding similarity between answer and quote, or an LLM judge.
- **Defensive parsing.** Valid JSON can still be a list, or have non-string fields; `json.loads` raises on junk. `parse_answer` returns `(answer, quote)` or `None` and never crashes.
- **Fail open vs fail closed.** `"" in text` is True in Python, so an empty quote would pass a naive substring check. Check for empty first.
- **Strings are immutable.** `text.lower()` returns a new string; assign it.
- **Reference vs copy.** `a = b` shares one object; `dict(b)` is a new (shallow) copy.
- **Deployment boundary.** Render ships only `projects/day-27/awesome-project/`, so helper code must be copied into `assistant.py`, not imported from another day's folder (an import I added would have crashed the live app).
- **A strict check causes false refusals.** The note says `**Temperature:** Controls how random...`; the model quoted `Temperature controls how random...`. Strict matching rejected an honest quote. Fix: `normalize` lowercases and keeps only letters and digits, so markdown and punctuation can't matter.

## What was built

- `projects/day-42-grounding-check/verify.py`: `parse_answer`, `normalize`, `quote_in_context`, with 10 printed test cases (all as expected).
- `projects/day-42-grounding-check/try_prompt.py`: scratch script proving the JSON prompt (temperature gives a real quote; LoRA gives empty strings).
- `assistant.py`: the three helpers copied in; `answer_question` now asks for JSON, parses it, verifies the quote against the chunks, refuses otherwise, and only caches validated answers.

## Test evidence (local, 7 questions)

| Question | Result |
|---|---|
| what is temperature | answered from notes |
| what is RAG | answered |
| why must index and query use the same embedding model? | answered |
| how do I make repeated questions faster (vague) | answered |
| how does LoRA fine-tuning work | refused (was a fake-sourced answer) |
| what is the context window of GPT-4 | refused (was a fake-sourced answer) |
| who won the 2018 World Cup? | refused |

## Real mistakes made

1. Copied `...` placeholders literally into an API call; used variables (`context`, `query`) that did not exist in the scratch file.
2. Put the system text inside the user dict as an extra key instead of a separate `role: system` message.
3. Predicted the verifier would return False for a real but irrelevant quote (it returns True).
4. Inverted an `isinstance` check inside `normalize`, which broke every call; no tests existed to catch it.
5. Added `from verify import ...` to the live app (would have crashed on Render with `ModuleNotFoundError`).
6. Called `quote_in_context` with one argument and treated its True/False as the answer text.
7. On refusal paths returned a string instead of the dict `main.py` expects; showed raw JSON instead of `answer_text` on success.
8. Garbled the system prompt by joining strings without spaces and dropping the start of a sentence.

All are in `evals/mistakes-log.md`.

## Where we left off (Day 43)

1. Add LoRA and GPT-4 to `projects/day-31-deployed-evals/eval_questions.json` as should-refuse cases (ids 14 and 15), then re-run the live eval after deploying for a before/after number.
2. Retry the model call once when `parse_answer` returns `None` (the plan said retry-once; the code currently refuses immediately).
3. Test whether the answer-vs-quote word-overlap check is worth adding (the real-but-irrelevant-quote weakness).
4. Fix Q1's `logits` keyword in the live eval (verify the answer first).
5. The refusal paths skip `_usage_info`, so the cost of a refused call is not recorded; decide whether to track it.
