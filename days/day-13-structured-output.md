# Day 13 — Structured JSON Output from RAG

> Previous: [Day 12 — RAG Improved](day-12-rag-improved.md)

## What This Day Is About

Modified the RAG system to return structured JSON instead of free text. The LLM now outputs a machine-readable object with `answer`, `confidence`, and `sources` fields instead of a raw prose response. This is how real AI APIs work — structured output connects AI to downstream systems.

---

## 1. The Result

**Before (free text):**
```
Cosine similarity measures the angle between two vectors, indicating their
directional similarity regardless of vector length...
```

**After (structured JSON):**
```
Answer: Cosine similarity measures the angle between two vectors, considering direction but not magnitude.
Confidence: high
Sources: day-09-semantic-search.md, day-03-corrections-and-gaps.md, day-07-pipeline-hands-on.md
```

Same retrieval, same model, completely different output shape — changed only by the system prompt.

---

## 2. What Changed from Day 12

Three changes to `rag_v2.py`:

### Change 1 — System prompt instructs JSON output

```python
{"role": "system", "content": "You are a helpful assistant. Answer only from the provided context. You MUST respond with ONLY a valid JSON object in this exact format, no other text: {\"answer\": \"your answer here\", \"confidence\": \"high or medium or low\"}"}
```

The system prompt is the only lever you have to control output format. This is how every AI API that returns structured data works — the instruction is in the prompt, not in the model.

### Change 2 — Disable streaming

```python
json={"model": "phi3:mini", "messages": conversation_history, "stream": False}
```

Streaming sends tokens one by one — you can't parse JSON until you have the complete string. With `stream: False`, Ollama waits until generation is complete and returns the full response as one JSON object.

### Change 3 — Parse the response + handle markdown fences

Small models often wrap JSON in markdown code blocks (` ```json ... ``` `) even when told not to. The parser strips these before parsing:

```python
full_response = response.json()["message"]["content"].strip()
# Strip markdown code fences
if full_response.startswith("```"):
    full_response = full_response.split("```")[-2]
    full_response = full_response.lstrip("json").strip()
# Extract just the JSON object if model added extra text
start = full_response.find("{")
end = full_response.rfind("}") + 1
if start != -1 and end > start:
    full_response = full_response[start:end]

try:
    parsed = json.loads(full_response)
    print(f"\nAnswer: {parsed['answer']}")
    print(f"Confidence: {parsed['confidence']}")
    print(f"Sources: {', '.join(sources)}")
except (json.JSONDecodeError, KeyError):
    print(f"\n[Model did not return valid JSON. Raw response:]")
    print(full_response)
```

---

## 3. Why Structured Output Matters

### Free text is for humans. Structured output is for machines.

With free text, you can only display the answer to a user. With structured output, your code can:

- **Show confidence badges** in a UI — green for high, yellow for medium, red for low
- **Filter answers** — don't show responses with `"confidence": "low"` to users
- **Log structured data** — store `{query, answer, confidence, sources, timestamp}` in a database
- **Route to fallbacks** — if confidence is low, escalate to a human or a larger model
- **Feed into other systems** — the answer field can be passed to another API call

This is the bridge between "AI generates text" and "AI as a component in a real application."

### The output schema used

```json
{
  "answer": "...",
  "confidence": "high | medium | low"
}
```

Sources come from the retrieval step (already computed), not from the LLM.

---

## 4. Small Models and Format Compliance

phi3:mini sometimes ignores the JSON instruction:
- Wraps JSON in markdown code blocks (` ```json ... ``` `)
- Adds explanation text after the JSON object
- Uses different key names than specified

This is a **small model limitation**. Larger models (GPT-4, Claude, Gemini) follow format instructions much more reliably. The same code with a better model would produce clean JSON every time.

**The solution for production:** Use a model with better instruction following, or use a model API that has a native `response_format: json` parameter (OpenAI, Gemini both support this — it forces the output to be valid JSON at the infrastructure level, not just via prompting).

---

## 5. Retrieval Quality vs Answer Quality — Confirmed Again

For the temperature query:
- Retrieval was correct: Day 02's temperature table ranked 1st and 2nd ✅
- Answer was imprecise: said "low to medium" instead of the specific value "0.1–0.3" ❌

The structured output format revealed this clearly — `confidence: high` was returned even though the answer was vague. This shows that phi3:mini's confidence self-assessment isn't reliable.

**In production:** You'd compute confidence from the retrieval scores, not let the model self-assess:
```python
top_score = result[0][2]
confidence = "high" if top_score > 0.7 else "medium" if top_score > 0.5 else "low"
```

---

## 6. The Full Pipeline Now

```
User query
    ↓
Embed query (all-minilm)
    ↓
Cosine similarity against 467 cached chunks
    ↓
Deduplicate by source, take top 5
    ↓
Score threshold check (< 0.4 → refuse)
    ↓
Build context string from top 5 chunks
    ↓
Send to phi3:mini with JSON format instruction
    ↓
Strip markdown fences, extract JSON object
    ↓
Parse JSON → print Answer, Confidence, Sources
```

---

## Key Takeaways

**System prompt controls output format.** "Respond in JSON" in the system prompt is how you get structured output. Same model, different instruction, different output shape.

**Streaming must be disabled for JSON output.** You need the complete string to parse JSON. `stream: False` makes Ollama wait for the full response.

**Small models are unreliable at format compliance.** phi3:mini wraps JSON in code blocks, adds extra text, changes key names. Build defensive parsing.

**Structured output enables AI as a system component.** Free text is a dead end for automated systems. Structured output lets you filter, log, route, and connect AI to real applications.

**Confidence from retrieval scores is more reliable than self-assessed confidence.** The model claiming "high confidence" means nothing. The retrieval score tells you objectively how well the context matched the query.

---

## One-Line Summaries

**Structured output:** System prompt + `stream: False` + `json.loads()` = machine-readable AI responses.

**Format compliance:** Small models ignore format instructions — always strip markdown fences and extract JSON defensively.

**stream: False:** Disables token-by-token delivery so you get one complete response object to parse.

**Computed confidence:** `top_score > 0.7 → high` is more reliable than asking the model to self-assess.

---

## Revision Questions

1. **What two things do you change in the code to get JSON output instead of free text?**
2. **Why must streaming be disabled when using JSON output?**
3. **phi3:mini returned ` ```json {"answer": "..."} ``` ` instead of `{"answer": "..."}`. What is the problem and how do you fix it?**
4. **You want to show a confidence badge in your UI. Why is computing confidence from retrieval scores better than letting the model self-assess?**
5. **Name 3 things you can do with structured output that you can't do with free text.**
6. **The model returns `{"response": "...", "certainty": "high"}` instead of `{"answer": "...", "confidence": "high"}`. Why did this happen? How do you prevent it?**
7. **OpenAI's API has a `response_format: {"type": "json_object"}` parameter. What problem does this solve that prompting alone doesn't?**
8. **You want to store every query and answer in a database. Why does structured output make this easier than free text?**
