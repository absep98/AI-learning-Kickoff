# Day 05: Inference, Local Models, API Lifecycle, and the AI Engineer Mindset

This was a deep reading session — no code shipped, but a lot of critical concepts clicked. The goal shifted from "play with playground" to understanding the full picture: how AI apps actually work under the hood, what local vs cloud inference means, and what the practical AI engineering stack looks like.

---

## 1. The Inference Pipeline — What Actually Happens When You Call an LLM

When you send a prompt to any LLM (cloud API or local), this is the full lifecycle:

```
Your App (code / playground / terminal)
     ↓
Prompt (text you send)
     ↓
API / Local Server (receives HTTP request)
     ↓
Tokenization (text → token IDs)
     ↓
Model Inference (tokens → transformer → attention → probability distribution → sampling)
     ↓
Response generated token-by-token
     ↓
Response returned to your app
```

### What "inference" means

**Training** = teaching the model (billions of dollars, weeks of compute).  
**Inference** = using the trained model to generate output (what happens every time you send a prompt).

Every time you use ChatGPT, Claude, or Gemini — that is inference. The model is not learning from your prompt. It is running its trained weights against your input to predict output.

### Why this matters

- Inference costs money (cloud) or compute (local).
- Longer prompts = more tokens = slower inference = higher cost.
- Every token in the context window is processed by the attention mechanism against every other token — that is why cost grows with context size.

---

## 2. LLMs Are Stateless — Memory Is an Illusion

This is one of the most important things to understand.

**LLMs have no memory between requests.**

When you use ChatGPT and it "remembers" your earlier message, that is NOT the model remembering. The app is re-sending your entire conversation history with every new request.

```
Request 1:
  messages: [
    { role: "user", content: "My name is Abhi" }
  ]

Request 2:
  messages: [
    { role: "user", content: "My name is Abhi" },
    { role: "assistant", content: "Nice to meet you, Abhi!" },
    { role: "user", content: "What is my name?" }
  ]
```

The model sees the FULL history every time. It does not "remember" — the application re-sends everything.

### Why this matters practically

- **Context window fills up** — as conversation grows, older messages must be dropped or summarised.
- **Token costs grow linearly** — every message in history gets re-processed on each request.
- **"Memory" is an engineering problem**, not an AI problem — the app developer manages it.
- **This is why ChatGPT sometimes "forgets"** — your conversation outgrew the context window and older messages were silently dropped.

### Chat history format (standard across most APIs)

```json
[
  { "role": "system", "content": "You are a helpful assistant." },
  { "role": "user", "content": "What is Go?" },
  { "role": "assistant", "content": "Go is a statically typed..." },
  { "role": "user", "content": "How do goroutines work?" }
]
```

Three roles:
- **system** — sets the model's persona/behavior (processed first, shapes all responses)
- **user** — your messages
- **assistant** — the model's previous responses

---

## 3. System Prompts — Shaping Model Behavior

A system prompt is an instruction that tells the model HOW to behave, before the user says anything.

```
System: "You are a sarcastic senior Go developer. Be concise."

User: "What is a slice?"

AI: "It's a dynamically-sized view into an array. Basically what you
     wish arrays were in every other language. You're welcome."
```

Without the system prompt, the same question gets a generic, textbook-style answer. With it, the model adopts a completely different personality.

### Why system prompts matter for AI engineers

- **Product differentiation** — the system prompt defines your AI product's personality.
- **Output format control** — "Always respond in JSON" or "Always give exactly 3 bullet points."
- **Safety guardrails** — "Never discuss topics outside of cooking recipes."
- **Domain expertise** — "You are an expert in Kubernetes troubleshooting."

The system prompt is not optional decoration. It is a core part of the AI application architecture.

---

## 4. Key API Parameters Every AI Engineer Must Know

### temperature

Controls randomness. Already covered deeply in Day 02, but now with practical context:

| Value | Use case |
| --- | --- |
| 0.0–0.3 | Code generation, SQL, JSON output, factual Q&A |
| 0.5–0.7 | General conversation, summaries, explanations |
| 0.9–1.5 | Brainstorming, creative writing, storytelling |

### max_tokens (or maxOutputTokens)

Limits how many tokens the model can generate in its response.

```
max_tokens: 50  → short, truncated answer
max_tokens: 500 → full paragraph
max_tokens: 2000 → detailed essay
```

This is a **cost and speed control lever**. Set it low for chatbots, higher for content generation.

### model

Which model to use. Determines:
- Intelligence level
- Speed
- Cost
- Context window size

Examples:
- `gemini-2.0-flash` — fast, cheap, good enough for most tasks
- `gemini-1.5-pro` — smarter, slower, more expensive
- `gpt-4o` — OpenAI's fast flagship
- `claude-sonnet-4-20250514` — Anthropic's balanced model

### stream

Whether to receive the response token-by-token (streaming) or all at once.

- `stream: false` → wait for full response, then display
- `stream: true` → tokens appear one-by-one as they are generated (the "typing" effect in ChatGPT)

Streaming is better for UX but slightly more complex to implement.

---

## 5. Local vs Cloud Inference

### Cloud inference (OpenAI, Anthropic, Google)

```
Your code → HTTPS request → cloud server → giant GPU cluster → response
```

**Pros:** Powerful models, no hardware requirements, always available.  
**Cons:** Costs money, rate limits, data leaves your machine, vendor dependency.

### Local inference (Ollama, LM Studio, llama.cpp)

```
Your code → HTTP request → localhost → your own CPU/GPU → response
```

**Pros:** Free, private, no rate limits, full control, works offline.  
**Cons:** Slower, limited by your hardware, smaller models only.

### Ollama — the simplest local inference tool

Ollama wraps model downloading and inference into a simple CLI:

```bash
ollama run phi3:mini      # start chatting with Phi-3 Mini
ollama run gemma:2b       # or Google's Gemma 2B
ollama run llama3.2       # or Meta's Llama 3.2
```

It also runs a local HTTP server at `http://localhost:11434` that your code can call — same as calling a cloud API but on your own machine.

### Which to use for learning?

**Both.** Cloud APIs teach you the production flow (API keys, SDKs, cost management). Local models teach you inference behavior (speed, memory, model quality differences). Start with whichever has less friction.

---

## 6. Model Parameters — What "7B" Means

When you see "Llama 3 8B" or "Phi-3 Mini 3.8B," the number is the parameter count.

**Parameters** = the billions of adjustable weights inside the neural network. These are the "knobs" the model learned during training.

| Model | Parameters | RAM needed | Quality |
| --- | --- | --- | --- |
| TinyLlama | 1.1B | ~1 GB | Basic, fast |
| Phi-3 Mini | 3.8B | ~2-4 GB | Surprisingly capable |
| Gemma 2B | 2B | ~2 GB | Good for experiments |
| Llama 3 8B | 8B | ~5-8 GB | Strong general purpose |
| Llama 3 70B | 70B | ~40+ GB | "Sell kidney for GPUs" tier |

### What more parameters mean

- **Smarter** — can handle more complex reasoning and nuance
- **Slower** — more computation per token
- **Heavier** — more RAM/VRAM needed
- **More expensive** — whether in cloud cost or local hardware

### Key insight for AI engineers

You do NOT always need the biggest model. For many tasks (summarisation, simple Q&A, formatting, classification), a small model works fine and is 10x cheaper/faster. Choosing the right model size for the task is an engineering decision, not a "bigger is better" decision.

---

## 7. The AI Application Engineering Stack

This is the practical toolkit. Not ML research — AI application building.

| Skill | What it is | Why it matters |
| --- | --- | --- |
| Prompt engineering | Crafting effective prompts + system prompts | Controls output quality |
| API integration | Calling LLM APIs from code | Core of any AI app |
| Chat history management | Maintaining conversation context | Makes chatbots work |
| Structured output | Getting JSON/data from LLMs | Connects AI to real systems |
| Embeddings APIs | Converting text to vectors | Powers search and RAG |
| Vector databases | Storing and searching embeddings | Foundation of RAG |
| Chunking strategies | Splitting documents into pieces | Determines retrieval quality |
| Function/tool calling | Letting LLMs invoke your code | Makes AI agents work |
| Streaming | Token-by-token response delivery | Better user experience |
| Cost management | Token counting, model selection, caching | Production viability |

This is NOT:
- Training models from scratch
- Writing CUDA kernels
- PhD-level ML research

This IS:
- Building products that use AI as a component
- The highest-leverage skill for software engineers in 2025-2026

---

## 8. The Build Path — What to Build and in What Order

### Phase 1: Terminal Chatbot

```
Your code → LLM API → print response
```

Teaches: API lifecycle, prompts, responses, temperature, tokens, statelessness.

### Phase 2: Semantic Search

```
Store documents → embed them → query by meaning → retrieve matches
```

Teaches: embeddings become REAL, not theoretical. The "aha" moment.

### Phase 3: Mini RAG

```
PDF → chunk → embed → vector DB → query → retrieve → LLM answers
```

Teaches: the full modern AI app stack in one project.

### Phase 4: Full AI Knowledge Assistant

```
Upload docs → ask questions → get answers with citations → conversation memory
```

Teaches: everything combined. This single project covers embeddings, RAG, context windows, token management, vector DBs, prompting, APIs, backend engineering, and frontend integration.

### The rule

**Build each phase before reading about the next one.** Theory after building sticks 10x better than theory before building.

---

## 9. What NOT to Learn Yet

These are real things but premature right now:

| Topic | Why not yet |
| --- | --- |
| LangChain / LlamaIndex | Frameworks that hide the fundamentals — learn the fundamentals first |
| AI Agents | Requires solid understanding of tools + prompting + memory first |
| Fine-tuning | Expensive, complex, rarely needed for app builders |
| Multi-agent systems | Advanced orchestration — need single-agent basics first |
| CUDA / GPU programming | Infrastructure concern, not application concern |
| Model training | Requires ML research background, not needed for AI apps |

The trap: consuming content about advanced topics creates an illusion of understanding without the foundation to actually use any of it. Build basic systems first — advanced concepts become obvious once you have the fundamentals.

---

## Key Takeaways

**Inference** = using a trained model to generate output. This is what happens every API call.

**LLMs are stateless** = no memory between requests. Chat history is re-sent every time by the app, not remembered by the model.

**System prompts** = behavior shaping instructions. They define your AI product's personality and constraints.

**Local vs cloud** = trade-off between cost/privacy (local) and power/convenience (cloud). Both are useful for learning.

**Model size** = parameters. More parameters = smarter but slower and heavier. Pick the right size for the task.

**The AI engineer stack** = prompting + APIs + embeddings + vector DBs + RAG + structured output. This is the high-leverage skillset.

**Build path** = chatbot → semantic search → RAG → knowledge assistant. Each phase makes the next one make sense.

---

## One-Line Summaries

**Inference:** Running a trained model against your input to get output — the model is not learning, it is predicting.

**Statelessness:** LLMs forget everything between requests — "memory" is the app re-sending chat history every time.

**System prompt:** An instruction that shapes HOW the model behaves before the user says anything.

**Parameters:** The billions of trained weights inside a model — more = smarter but heavier.

**AI engineer vs ML researcher:** Build products with AI (engineer) vs build new AI models (researcher). You want engineer.
