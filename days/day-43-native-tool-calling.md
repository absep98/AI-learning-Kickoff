# Day 43 - Native Tool Calling: The Model Asks, Your Code Runs

**Status: first full round trip working in a scratch script (`projects/day-43-tool-calling/try_tools.py`). Not yet wired into the live assistant.**

## Also done at the start of the day (RAG close-out)

- Confirmed the Day 42 grounding check on production: temperature answers; LoRA and GPT-4 context say "No relevant notes found".
- Added LoRA and GPT-4 context to the live eval as should-refuse (ids 14, 15). Live eval: 14/15. The one failure was Q1 (`logits` keyword), a too-narrow check on a correct answer, so the keyword became `random`. Not re-run yet.

## The idea

My Day 25 planner (`model_plan_action`) asks for one action string in plain text, then cleans it (`strip`, `lower`, remove quotes) and checks it is in `ALLOWED_ACTIONS`, falling back to rules if not. Native tool calling replaces that:

1. Each tool is described as a schema: `name`, `description`, `parameters` (what inputs, which are `required`).
2. The model does not answer; it returns `content=None` and a `tool_calls` list.
3. Each tool call has `function.name`, `function.arguments` and an `id`.
4. My code runs the tool, then makes a second call so the model can see the result.

The big difference from the planner: the model can pass an input (`{"day": 42}`), not only pick a desk.

## What I learned

- `tools=TOOLS` is its own argument to `create(...)`, separate from `messages`. `TOOLS` is a list of schema dicts, not a dict keyed by tool name.
- `description` is what the model reads to decide when to use a tool. A typo (`descriptions`) silently removes it.
- `arguments` is a JSON **string**, so `json.loads(call.function.arguments)["day"]`. `tool_calls` is a **list** (several calls are possible).
- The API is stateless, so the second call must contain three parts:
  1. the original user message
  2. the model's own assistant message with its `tool_calls`, passed as it came (no wrapper dict)
  3. `{"role": "tool", "tool_call_id": call.id, "content": <text>}`
- `tool_call_id` must equal `call.id` so the model can match a result to its request.
- `Path.glob("day-NN-*.md")` finds files by pattern; `f"{day:02d}"` pads to two digits (`0.2d` is a ValueError).
- The fallback in `model_plan_action` covers an unusable model reply (empty, a sentence, not in `ALLOWED_ACTIONS`) or an API error, not a query "without a desk" (`answer_question` is the catch-all).

## Real mistakes made

1. Wrapped the tool schema one level too deep (`[{"read_day_note": {...}}]`); typo `descriptions`.
2. Left old Day 42 code in the scratch file, and `from verify import ...` would have failed (cross-folder import again).
3. Put `tools` inside the `messages` list.
4. Used a variable called `note` for the day number, then for the text; the f-string then inserted the whole note into the user message.
5. Wrapped the assistant message as `{"messages": ...}`, which the API rejected (`input does not contain the discriminator property 'role'`).
6. Format spec `{day:0.2d}` and an extra `, day` argument to `glob`.
7. Thought the planner fallback was for queries without a matching desk.

## Where we left off

- Revision block deferred (owed next session, first thing).
- Not yet done: wrap a loop (the model may return several tool calls, or none), validate the tool name and arguments in code, replace `model_plan_action` with a tool-calling version, then look at MCP.
