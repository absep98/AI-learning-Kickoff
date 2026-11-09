# Day 44 - Tool Calls Come One At A Time, And Models Can Write Them Wrong

**Status: partly done.** Learned why a single round trip is not enough and met a real model failure. The loop itself is not built yet.

## What happened

1. Added a second tool, `get_time` (no inputs), next to `read_day_note` in `projects/day-43-tool-calling/try_tools.py`.
2. Asked: "what did I learn on day 42, and what time is it?". Call 1 returned **one** tool call (`read_day_note`), not two. The model asked for the tools one at a time.
3. Call 2 (after sending the note back) failed with `400 tool_use_failed`: `openai/gpt-oss-20b` tried to call a tool named `get_time<|channel|>commentary`, a leaked internal token. Groq checks tool names against `tools`, found no match and rejected it. Same error on every re-run, because `temperature=0` makes it deterministic, so retrying identical input cannot help.
4. Moved the model name into one constant `MODEL`. `llama-3.3-70b-versatile` returned 404 (model retired). Listed the models my key can use (`client.models.list()`), tried `qwen/qwen3.8-27b`: call 2 worked and asked for `get_time`.

## Concepts learned

- A model may request tools one at a time, so a fixed "two calls" script stops too early. The real shape is a loop (like Day 18): ask the model, if it returns `tool_calls` run them and append results, ask again, stop when it returns plain `content`. Cap the loop (`MAX_STEPS`).
- Why call 2 must include the model's own `tool_calls` message: the API is stateless, so otherwise the tool result's `tool_call_id` points at nothing.
- Call 1 returns a request to run a tool (`content=None`), not an answer. Your code does the work between the two calls.
- A model can write a malformed tool call. Retrying identical input at temperature 0 repeats the failure. Change one variable (model, tool, prompt) and re-run.
- Models get retired (Day 36 again). List the real models from the API instead of guessing; keep the model name in one constant.
- `tools=` is its own argument, `TOOLS` is a list of schema dicts, one dict per tool.

## Real mistakes made

1. Un-commented the second API call but left the code that builds `messages` commented out (NameError).
2. Kept an old user message in `messages` instead of the new question.
3. Said "avoid giving no response" for the planner fallback; it covers an unusable reply or an API error.
4. Wrote "process the string" instead of `json.loads` for `arguments`.
5. Could not say why the model's own `tool_calls` message must be in call 2 (statelessness).

## Where we left off

- Add `get_time()` and a dispatch (`if name == "read_day_note" ... elif name == "get_time" ...`).
- Build the loop with a step cap; validate the tool name and arguments in code before running anything; wrap the model call in `try/except`.
- Then replace `model_plan_action` with a tool-calling version, then MCP.
- Revision block owed (deferred 2 sessions in a row). Do it first next session.
