# Day 06: Hands-On With Local Inference — Ollama Experiments

Theory from Day 05 said a lot of things: "LLMs are stateless," "small models hallucinate more," "inference is slow locally." This day was about PROVING all of that by actually running a local model and watching what happens.

Installed Ollama, pulled `phi3:mini`, and ran experiments. Every concept from the notes became tangible.

---

## 1. What Happens When You Install and Run a Model

### The installation flow

```
Download Ollama (ollama.com)
     ↓
Install normally
     ↓
Verify: ollama --version
     ↓
Run: ollama run phi3:mini
     ↓
First run: downloads model (~2GB)
     ↓
Model stored locally on disk
     ↓
Model loaded into RAM
     ↓
Inference server starts
     ↓
Interactive chat session begins
```

### What is actually happening in RAM

When you run `ollama run phi3:mini`, the model's billions of parameters (weights) get loaded from disk into your RAM. These weights ARE the model — they are the patterns learned during training. The model sits in RAM the entire time you are chatting, which is why it uses 2-4 GB.

### Key insight

You are not "connecting to AI." You ARE running AI. The entire model is on your machine, in your RAM, doing math on your CPU. No internet required after download.

---

## 2. Observing Token-by-Token Generation

### What I saw

When asking `phi3:mini` a question, the response does not appear all at once. Words appear one by one, with a visible delay between each one.

### Why this happens

The model generates ONE token at a time:

```
Step 1: predict token 1 → "Redis"
Step 2: predict token 2 → " is"
Step 3: predict token 3 → " an"
Step 4: predict token 4 → " in"
Step 5: predict token 5 → "-memory"
...repeat hundreds of times
```

Each step requires running the ENTIRE model (all 3.8 billion parameters) once. On a CPU, each step takes measurable time. That is why you can watch the response being "typed."

### Why cloud models feel instant

Cloud providers use:
- **GPU clusters** — GPUs are massively parallel, running thousands of operations simultaneously
- **Optimized inference engines** — custom software to maximize speed
- **Batching** — processing multiple users' requests together
- **Specialized hardware** — TPUs, inference-specific chips

A local CPU processes tokens sequentially. A cloud GPU cluster processes them in parallel. That is the speed difference.

### What this teaches

- Inference has a real computational cost per token
- More output tokens = linearly more time
- Longer input prompts = more attention computation = slower
- This is why API pricing is per-token — you are paying for GPU time

---

## 3. Memory Test — Proving LLMs Are Stateless

### The experiment

```
Me: "My favorite language is Go"
[...several messages of normal conversation...]
Me: "What is my favorite language?"
```

### The result

It failed. Could not recall what I said earlier.

### Why this happened

This proves what Day 05 described theoretically: **LLMs do not inherently remember.**

In a well-built chat application (like ChatGPT), the app re-sends ALL previous messages with every new request. The model "remembers" because it literally sees the entire conversation again each time.

In some local setups:
- History may be trimmed to save tokens
- Context windows may be too small to hold the full conversation
- The chat interface may not pass full history properly
- Old messages may be summarised or dropped

### The deeper insight

**Memory is an APPLICATION feature, not a MODEL feature.**

```
What users think happens:
  User says something → AI stores it in brain → recalls later

What actually happens:
  User says something → App stores it in array → App re-sends entire array next time
  → Model sees everything fresh → Responds as if it "remembers"
```

This is why:
- Long conversations cost more tokens (history grows each turn)
- Eventually old messages MUST be dropped (context window fills up)
- "Forgetting" is not a bug — it is the natural consequence of running out of space on the whiteboard
- Building good memory management is an engineering challenge, not an AI problem

---

## 4. Code Quality Test — Small Model Limitations

### The experiment

Asked `phi3:mini` to write a Java BFS implementation.

### What I observed

- **Verbose** — way more explanation than needed
- **Weird formatting** — symbols and structure were off
- **Wrong characters** — `#` appearing in Java code where it does not belong
- **Bloated logic** — unnecessary steps, roundabout implementation
- **Hallucination** — confidently generating code patterns that are incorrect

### What this teaches

**Smaller models have weaker reasoning and coding precision.** They have fewer parameters, which means fewer "patterns" stored. Complex tasks like writing correct, idiomatic code require patterns the model simply does not have enough weights to represent well.

### The important comparison

| | Small model (phi3:mini, 3.8B) | Large model (GPT-4, Claude, 100B+) |
| --- | --- | --- |
| Speed (local) | Slow | Cannot run locally |
| Speed (cloud) | N/A | Fast |
| Code quality | Mediocre, hallucinations | Strong, mostly correct |
| Reasoning | Surface-level | Multi-step capable |
| Cost | Free (local) | Per-token (cloud) |
| Best for | Learning, prototyping, simple tasks | Production, complex tasks |

### The production lesson

This is exactly why real AI products use:

```
Small model + good retrieval (RAG) + tools + validation
```

instead of just:

```
Raw LLM alone
```

A small model that retrieves the right documentation can outperform a large model guessing from memory.

---

## 5. Prompt Sensitivity — Same Question, Different Results

### The experiment

```
Prompt 1: "Explain Redis"
Prompt 2: "Explain Redis like a senior backend engineer"
```

### What I observed

- Prompt 1 gave a generic, textbook-style explanation
- Prompt 2 gave a technical, opinionated, concise explanation with practical insights

Same model. Same knowledge. Completely different output quality and style.

### Why this matters for AI engineering

**The prompt IS the interface.** In traditional software, you design UIs and APIs. In AI applications, you design prompts. A well-crafted prompt is the difference between a useful product and a frustrating one.

### Prompt patterns observed

| Prompt style | Result |
| --- | --- |
| Plain question | Generic, safe, verbose |
| With persona ("like a senior engineer") | Technical, concise, opinionated |
| With constraints ("in 2 bullet points") | Focused, minimal |
| With format ("respond in JSON") | Structured, parseable |
| With context ("given this code...") | Relevant, specific |

The model does not "understand" these instructions the way humans do. It has seen millions of examples of each pattern in training and learned to reproduce the associated style. But the practical effect is the same — you can control the output dramatically through the prompt.

---

## 6. The Chat UI ≠ The Model

### The mental model shift

Before this day:
```
"Ollama chat" = AI
```

After this day:
```
"Ollama chat" = a thin wrapper that sends HTTP requests to a local API server
```

The terminal chat interface is NOT the model. It is a convenience layer. Under the hood:

```
You type text
     ↓
Chat UI formats it as JSON
     ↓
HTTP POST to localhost:11434/api/generate
     ↓
Ollama server runs model inference
     ↓
JSON response returned
     ↓
Chat UI prints the "response" field
```

### Why this matters

Once you understand this, you realise:
- You can replace the chat UI with YOUR code
- You can call the same API from Node.js, Python, a web app, a mobile app, anything
- The model is just an HTTP server — same as a database or any other backend service
- AI engineering is backend engineering with a probabilistic component

### The curl proof

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "phi3:mini",
  "prompt": "What is Redis?",
  "stream": false
}'
```

This returns raw JSON:

```json
{
  "response": "Redis is an open-source, in-memory data structure store...",
  "model": "phi3:mini",
  "total_duration": 8234567890,
  "eval_count": 142
}
```

Now the LLM is demystified. It is an API server that accepts text and returns text. Everything else is engineering around that.

---

## 7. The Compound AI System — Why Raw LLMs Are Not Enough

### The formula

```
Modern AI system = Model + Retrieval + Tools + Memory + UI
```

NOT:

```
Modern AI system = Giant LLM
```

### What each component does

| Component | What it does | Example |
| --- | --- | --- |
| **Model** | Generates text, reasons, synthesises | GPT-4, Claude, phi3:mini |
| **Retrieval** | Finds relevant information | RAG, semantic search, vector DB |
| **Tools** | Takes actions in the real world | API calls, database queries, calculators |
| **Memory** | Maintains conversation state | Chat history array, summarisation |
| **UI** | Presents results to user | Chat interface, dashboard, API |

### Why this matters

When you see a product like ChatGPT, Cursor, or GitHub Copilot working impressively, it is NOT just the LLM. It is:
- The model generating text
- Retrieval systems finding relevant code/docs
- Tool integrations executing code, searching the web
- Memory systems tracking conversation context
- UI/UX making it feel seamless

Understanding this architecture is what separates "AI users" from "AI builders."

### The implication for learning

You do not need to build the best model. You need to learn how to orchestrate these components. That is AI engineering.

---

## 8. Learning Phase Map — Where I Am Now

```
Phase 1: Terminology + Concepts     → DONE (Days 01-05)
Phase 2: Hands-on Model Exploration → IN PROGRESS (Day 06)
Phase 3: API Integration + Chatbot  → NEXT
Phase 4: Embeddings + Semantic Search
Phase 5: Mini RAG System
Phase 6: Full AI Application
```

### Phase 2 is about developing intuition

Not writing production code. Not building products. Just:
- Running models
- Observing behavior
- Breaking things
- Understanding what works and what fails
- Making abstract concepts concrete

This phase is where:
```
"I know the words"  →  "I understand the system"
```

And this transition only happens through hands-on experimentation.

---

## 9. Experiment Checklist — What to Test With Local Models

These experiments turn concepts into intuition:

### Speed experiments
- [ ] Ask a short question and time the response
- [ ] Ask the same question with a long context pasted before it — observe the slowdown
- [ ] Set `num_predict: 20` and see truncated output
- [ ] Set `num_predict: 500` and see the time difference

### Quality experiments
- [x] Ask for code (BFS) — observe hallucinations and formatting issues
- [x] Ask the same question with different personas — observe style changes
- [ ] Ask a math problem — observe incorrect but confident answers
- [ ] Ask something it cannot know (recent events) — observe hallucination vs refusal

### Memory experiments
- [x] Tell it a fact, chat for a while, ask about the fact — observe context failure
- [ ] Build up a 10+ message conversation — observe when quality degrades
- [ ] Ask "summarise our conversation" — see what it retained vs lost

### Prompt experiments
- [x] Plain question vs persona-prompted question — observe the difference
- [ ] Ask for JSON output — test format compliance
- [ ] Ask "think step by step" before a reasoning task — observe improvement
- [ ] Give contradictory instructions — observe which one wins

---

## Key Takeaways

**Local inference is real and visible.** You can watch the model generate tokens one by one. This makes token costs, context limits, and inference speed tangible instead of abstract.

**Memory is fake.** The model does not remember anything. Chat applications re-send the entire conversation history every time. Memory management is an engineering problem.

**Small models hallucinate more.** Fewer parameters = fewer learned patterns = more guessing. This is why retrieval (RAG) matters — give the model facts instead of making it guess.

**Prompts shape everything.** Same model, different prompt, completely different output. Prompt design is a core engineering skill, not a nice-to-have.

**Chat UI = HTTP API wrapper.** The terminal chat is just a convenience. Under the hood, it is HTTP requests and JSON responses — same pattern as any backend service.

**Modern AI = compound system.** Model + Retrieval + Tools + Memory + UI. No single LLM is the product. The orchestration is the product.

**Cloud speed vs local speed.** Cloud feels instant because of GPU clusters and optimised hardware. Local CPU inference is visibly slower but teaches you what is actually happening.

---

## One-Line Summaries

**Token-by-token generation:** Each token requires running the entire model once — that is why local inference is slow and cloud inference costs money per token.

**Memory is application-level:** The model sees a fresh context every time — "remembering" is the app re-sending the full conversation history.

**Small model limitations:** Fewer parameters = weaker reasoning, more hallucination, worse code quality. But good enough for learning and prototyping.

**Prompt sensitivity:** Same knowledge, different prompts, completely different outputs. The prompt IS the interface for AI applications.

**Chat UI demystified:** The chat terminal is just HTTP POST to localhost:11434 → JSON response. Any code can replace it.

**Compound AI systems:** Model + Retrieval + Tools + Memory + UI = modern AI product. Raw LLM alone is not enough.
