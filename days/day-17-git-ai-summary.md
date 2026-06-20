# Day 17: Git AI Summary CLI

**Date:** June 20, 2026  
**Focus:** Build `git-ai-summary` CLI tool using structured JSON output + cloud API workflow  
**Outcome:** ✅ Complete - Functional end-to-end CLI with mode support and Groq integration

## What We Built

A command-line tool that analyzes Git diffs using Groq's LLM API and outputs structured summaries with suggested commit messages.

### Architecture

```
git_ai_summary.py
├── get_diff(mode)           → Captures git diff via subprocess
│   ├── unstaged: git diff
│   ├── staged: git diff --cached
│   └── both: combines both
├── summarize_diff(diff, mode) → Calls Groq API with JSON schema
│   ├── System prompt: JSON-only response requirement
│   ├── Truncate diff to 12K chars
│   ├── Parse JSON + extract from markdown fences
│   └── Fallback error handling
└── main(mode)               → Orchestrates flow, prints formatted output
    └── Output: What Changed | Risky Changes | Commit Message
```

### Technologies Used

- **Groq Cloud API:** llama-3.1-8b-instant model (temperature=0)
- **Subprocess:** Git integration via `git -C <path> diff`
- **JSON Parsing:** Schema-based structured output with fallbacks
- **Python Dotenv:** API key management from .env

## Key Functions

### `get_diff(mode)`
- Captures unstaged, staged, or both diffs
- Uses `subprocess.run()` with `capture_output=True` for clean output
- Combines diffs with separator for "both" mode
- Returns empty string if no changes

### `summarize_diff(diff_text, mode)`
- Truncates diff to 12K chars (API safety)
- Calls Groq with 2 constraints:
  1. System: "Respond with ONLY valid JSON in this exact shape: {...}"
  2. User: Includes Mode context and diff length
- Parses JSON, handles markdown fence wrapping
- Fallback: Returns raw response + error marker if JSON parse fails

### `main(mode)`
- Validates mode (unstaged/staged/both)
- Gets diff via `get_diff()`
- Returns early if no changes
- Calls `summarize_diff()` and formats 3-section output
- Handles None values gracefully

## Mode Support

| Mode | Command | Behavior |
| --- | --- | --- |
| unstaged | `python git_ai_summary.py unstaged` | Uncommitted changes only |
| staged | `python git_ai_summary.py staged` | Staged changes only |
| both | `python git_ai_summary.py both` | Both combined with separator |
| default | `python git_ai_summary.py` | Defaults to unstaged |

## Output Format

```
=== What Changed ===
[One-sentence or paragraph summary]

=== Risky Changes ===
- [Concrete risk 1]
- [Concrete risk 2]
- No major risks identified (if empty)

=== Suggested Commit Message ===
[Conventional commit message]
```

## Files Created

- `git_ai_summary.py`: Main CLI script
- `requirements.txt`: Dependencies (groq, python-dotenv)
- `README.md`: Usage documentation

## Lessons Learned

1. **Subprocess + Git Integration:** Using `subprocess.run()` with `capture_output=True` safely captures git output without piping shell directly
2. **JSON Schema in Prompts:** Explicit system message ("Respond with ONLY valid JSON in shape: {...}") reduces hallucination vs. implicit expectations
3. **Markdown Fence Handling:** LLMs sometimes wrap JSON in ```json ... ``` even with temperature=0. Must strip before parsing.
4. **Truncation Strategy:** Capping diff at 12K chars prevents token overflow while maintaining enough context for meaningful analysis
5. **Fallback JSON Parsing:** Try-except with fallback return preserves tool usability even on parse failures

## Challenges & Resolutions

| Challenge | Resolution |
| --- | --- |
| Groq rejecting message dict keys | Fixed: Moved Mode/Diff length into single content string with newlines |
| JSON wrapped in markdown fences | Added fence detection + extraction logic |
| Generic risk hallucinations | Improved system prompt specificity (still minor — model tends to generic security warnings) |
| No diff / empty changes | Early return with "No changes found." message |

## Testing Coverage

- ✅ Unstaged mode: Captures uncommitted changes
- ✅ Staged mode: Captures staged-only changes
- ✅ Both mode: Combines both with separator
- ✅ No changes: Early exit with message
- ✅ Invalid mode: Error message + early exit
- ✅ JSON parse error: Fallback to raw response + error marker

## Dependencies

```
groq>=0.4.1
python-dotenv>=1.0.0
```

## Next Steps

- Optional: Refine prompt to reduce generic risk warnings (requires evidence-based risk filtering)
- Optional: Add diff filtering (ignore vendor files, node_modules, etc.)
- Optional: Store summaries in JSON log for historical tracking
