# git-ai-summary

AI-powered Git diff summarizer. Analyzes your changes and suggests commit messages.

## Usage

```bash
python git_ai_summary.py [mode]
```

Modes:
- `unstaged` (default): Summarize uncommitted changes
- `staged`: Summarize staged changes
- `both`: Show both unstaged and staged

## Output

- What Changed: Summary of modifications
- Risky Changes: Potential issues to review
- Suggested Commit Message: AI-generated commit message

## Requirements

See requirements.txt