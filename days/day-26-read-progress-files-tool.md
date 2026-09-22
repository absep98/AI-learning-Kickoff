# Day 26 — Third Tool: read_progress_files

**DRAFT — written retroactively from actual commits/tests, review and personalize before treating as final.**

**Goal:** Add a third real tool to `repo_assistant.py` so questions about current progress/day are answered from real data, not RAG guessing — and prove the router scales past two actions.

---

## What Was Built

- `read_progress_files()` — reads `progress.md`, extracts the `**Current Day:**` and `**Main Goal:**` lines, returns them directly.
- Updated `model_plan_action`'s system prompt to list all three actions (`answer_question`, `check_git_status`, `read_progress_files`) with a short description of when to use each.
- Updated `plan_action`'s rule-based fallback to also check for "day"/"progress"/"roadmap" keywords.
- Added the routing branch in `__main__`'s if/elif chain.

## A Real Bug This Exposed

Before this tool existed, asking `"what day am I on"` silently fell through to `answer_question` (the only fallback action at the time), which retrieved random note chunks mentioning "Day 03" and answered from those — a confidently wrong, hallucinated answer with real citations attached. This is the exact failure mode RAG systems have when there's no tool for a question that isn't actually answerable from the document corpus.

## Test Evidence

- `"what day am I on"` → correctly routed to `read_progress_files`, returned the real `**Current Day:**` / `**Main Goal:**` lines from `progress.md` — no more hallucination.

## File Updated

- `projects/day-24-repo-assistant/repo_assistant.py`

## Key Learning

A RAG system without a way to say "I don't know" or "this isn't in my documents" will confidently retrieve *something* and answer from it, even when it's the wrong something. Adding a dedicated tool for a known question type is often a better fix than trying to make retrieval smarter.

## Next Step

`repo_assistant.py` is feature-complete as a CLI. Decide: deepen it further, or wrap it as a deployable web feature for a portfolio-worthy demo.
