# AI Learning Progress Log

Started: April 30, 2026

Use this file as the day-to-day working journal for the AI roadmap. Keep the main roadmap stable, and update this file with what you actually did, learned, struggled with, and will do next.

## Current Focus

**Phase:** Month 1 - Foundation And First AI Tool  
**Current Day:** Day 5 (complete) → Day 6 next  
**Main Goal:** Build terminal chatbot (first real code that calls an LLM).

## Progress Summary

| Area | Status |
| --- | --- |
| LLM basics | ✅ Complete |
| Tokens | ✅ Complete |
| Context window | ✅ Complete (deep) |
| Temperature | ✅ Complete |
| Embeddings | ⚠️ Corrected (was mixing with token prediction) |
| Internal pipeline | ⚠️ Corrected (was missing transformer/attention stage) |
| RAG | ❌→✅ Corrected (was fundamentally wrong — see Day 3) |
| Search vs LLM | ⚠️ Corrected (retrieve vs generate) |
| LLMs good at | ✅ Complete (10 categories) |
| LLMs bad at | ✅ Complete |
| Notes written | ✅ Complete |
| Concepts in own words | ✅ Complete |
| Day 1 complete | ✅ |
| Day 2 complete | ✅ |
| Day 3 complete | ✅ (knowledge test + corrections) |
| First API call | ✅ (via AI Studio Playground) |
| Day 4 complete | ✅ |
| Inference lifecycle | ✅ Complete |
| LLM statelessness | ✅ Complete |
| System prompts | ✅ Complete |
| API parameters | ✅ Complete (temperature, max_tokens, model, stream) |
| Local vs cloud inference | ✅ Complete |
| Model parameters (B) | ✅ Complete |
| AI engineer stack | ✅ Complete |
| Day 5 complete | ✅ (deep reading session) |
| Terminal chatbot | 🔲 Day 6 |

## Day 1 - LLM Basics

**Date:** April 30 – May 5, 2026

### Goal

Build a beginner-level mental model of LLMs so future API work makes sense.

By the end of today, you should be able to explain these in your own words:

- What an LLM is
- What tokens are
- What a context window is
- What temperature means
- What embeddings are at a high level
- What LLMs are good at
- What LLMs are bad at

### Time Budget

Target: 60-90 minutes

Suggested split:

- 45-60 minutes: watch/read one intro resource
- 20 minutes: write notes
- 10 minutes: explain concepts in your own words

### Resources

Pick one primary resource today. Do not jump between too many tabs.

Recommended options:

- Andrej Karpathy: Intro to Large Language Models
- Google Machine Learning Crash Course: Intro to Large Language Models
- Anthropic docs: Prompt engineering overview
- OpenAI docs: Text generation overview

### Checklist

- [x] Watch or read one beginner LLM introduction.
- [x] Write 10 bullet-point notes.
- [x] Explain tokens in your own words.
- [x] Explain context window in your own words.
- [x] Explain temperature in your own words.
- [x] Explain embeddings in your own words.
- [x] Write examples of tasks LLMs are good at.
- [x] Write examples of tasks LLMs are weak or risky at.
- [x] Write one question you still have.
- [x] Mark Day 1 complete.
- [x] Mark Day 2 complete.

### Notes

- An LLM is a giant neural network trained on text data to predict the next token — repeat that billions of times and you get something that looks like reasoning.
- The "T" in GPT stands for Transformer. The Attention mechanism inside Transformers lets the model decide which earlier words matter most when generating the next one.
- Training pipeline: raw text → tokenize → convert to vectors → train neural network → adjust billions of parameters → model that predicts text well.
- LLMs are called "large" because of massive training data, massive model size, and massive compute (thousands of GPUs).
- A token is usually a word, part of a word, punctuation, or code symbol. `unbelievable` → `["un", "believ", "able"]`.
- Rough rule: 1 token ≈ 0.75 English words. Code tends to use more tokens because symbols get split aggressively.
- LLM pricing is token-based: input tokens + output tokens = cost. A badly optimised prompt is a money leak.
- Context window = the whiteboard the model writes on. Everything — system prompt, chat history, your input, its output — must fit. Old content drops when full.
- Context window sizes: 8k (older), 32k, 128k, 1M+ tokens. Bigger = more expensive + slower but can handle entire codebases or books.
- Even inside the context window, recent tokens get more attention than old ones. Stuffing irrelevant text creates "information soup" and degrades quality.
- Temperature controls how the model samples the next token from its probability distribution. Low = picks safest option. High = spreads probability more evenly, allows surprising picks.
- Temperature does NOT add knowledge — same model, different caffeine level. Use low (0.1-0.3) for code/structured output, high (0.9-1.2) for creative writing.
- Embeddings are vectors (lists of floats) that encode meaning. Similar meaning → similar vectors → close in vector space. `king - man + woman ≈ queen` actually works in vector math.
- Embeddings power semantic search, RAG, recommendations, and clustering. They are the "understanding layer" between raw text and LLMs.
- The strongest AI systems are: LLM + tools + memory + retrieval + execution — not LLM alone.
- LLMs are probabilistic, not deterministic. They pick from a probability distribution each token — that is why the same prompt can give different outputs.

### Concepts In My Own Words

#### What is an LLM?

A Large Language Model is a neural network trained on enormous amounts of text. Its one core job is to predict the next token given all previous tokens. Do that billions of times across books, code, and conversations, and the model ends up compressing human language patterns into math. It looks like reasoning because good enough prediction eventually simulates reasoning. It is not "thinking" — it is an absurdly advanced autocomplete trained on humanity's text.

#### What are tokens?

A token is the basic unit an LLM processes. Not exactly a word — more like a word-piece. The tokenizer splits text into chunks the model can work with as numbers. `"ChatGPT is cool"` might become `["Chat", "G", "PT", " is", " cool"]`. This matters because pricing, speed, and the context window are all measured in tokens, not words. 1 token ≈ 0.75 English words.

#### What is a context window?

The context window is the AI's short-term working memory — a whiteboard of fixed size. Everything on it counts: system instructions, previous messages, your current prompt, and the model's reply. Once you hit the limit, old content gets erased and the model has no access to it. This is not emotional forgetting — the text literally no longer exists in its active memory.

Sizes vary: 8k (older models), 32k, 128k, even 1M+ tokens. Bigger context = more capability but also more cost and latency. Important subtlety: even within the window, recent and relevant tokens get more attention than old distant ones. Blindly stuffing 500 pages in creates "information soup" — this is why RAG was invented. Instead of dumping everything in, RAG retrieves only the relevant chunks and sends just those to the model.

#### What is temperature?

Temperature controls how the model picks the next token from its probability distribution. Every token prediction produces a ranked list like: coffee 50%, tea 30%, lava 0.01%. Temperature reshapes that list before sampling.

- **Low temperature (0.0–0.3):** Concentrates probability on the top choices. Output is stable, predictable, and focused. Use for code, SQL, structured JSON, APIs.
- **High temperature (0.9–1.5):** Flattens the distribution. Less obvious tokens become viable. Output is creative, varied, sometimes surprising. Use for brainstorming, storytelling, creative writing.
- Temperature does NOT change what the model knows — it only changes how adventurous the token selection becomes. Same brain, different caffeine level.
- Even at temperature 0, outputs may not be perfectly deterministic due to hardware parallelism and backend optimisations.

Practical guide: coding assistant → 0.1–0.3, customer support → 0.3–0.5, general chatbot → 0.7, creative writing → 0.9–1.2.

#### What are embeddings?

Embeddings are numerical vector representations that encode the meaning of text (or code, images, users, products) as a list of floats — usually 384, 768, or 1536 dimensions. The key property: similar meaning → similar vectors → close together in vector space. This is not keyword matching; it is meaning matching.

Famous example: `king - man + woman ≈ queen`. The vectors actually encode semantic relationships that arithmetic can manipulate.

How they power RAG:
1. Split documents into chunks.
2. Generate an embedding for each chunk (one API call per chunk).
3. Store in a vector database.
4. At query time, embed the user's question.
5. Find the nearest chunk embeddings by cosine similarity.
6. Send only those relevant chunks to the LLM as context.

Result: private company chatbot without retraining the model. Embeddings are the "understanding layer" of modern AI systems.

Distinction to keep clear: tokens = break text into processable pieces; embeddings = represent meaning numerically; LLM = predict next tokens.


### LLMs Are Good At

- **Language and conversation:** explaining, summarising, translating, rewriting, tutoring, brainstorming
- **Coding:** boilerplate, debugging, explaining code, refactoring, test generation, SQL, regex, learning new frameworks fast
- **Pattern recognition:** spotting structure, relationships, and intent from examples without explicit rules
- **Summarisation:** compressing PDFs, meetings, logs, research papers into bullet points without emotional damage
- **Text transformation:** formal → casual, notes → blog, code → explanation, paragraph → bullets — any format/style shift
- **Knowledge retrieval (with caveats):** history, science, programming, business — but not guaranteed accurate, not a database
- **Reasoning-style tasks:** step-by-step problem decomposition, logic patterns, interview-style questions (especially with "think step by step")
- **Generating synthetic data:** mock APIs, fake datasets, test cases, placeholder content
- **Semantic understanding:** meaning-based search and recommendations via embeddings + transformers
- **Learning acceleration:** dramatically reduces friction from "I want to build X" to "I shipped X" for solo devs and learners

### LLMs Are Weak Or Risky At

- **Hallucination:** stating wrong facts with complete confidence — the dangerous 5% genius/nonsense ratio
- **Exact arithmetic:** a tiny calculator beats an LLM on `187463 × 92827` every time
- **Guaranteed factual accuracy:** they are pattern predictors, not databases — combine with search/retrieval for truth-critical tasks
- **Long-term memory:** no persistent memory across sessions without explicit memory systems
- **True understanding:** simulating reasoning ≠ understanding; fails hilariously on simple logic it hasn't seen in training
- **Real-world grounding:** only knows the world through text and images, not direct experience
- **Reliability under ambiguity:** vague prompts produce wildly inconsistent results

The fix: LLM + tools + databases + search + calculators + memory systems = the strong production pattern.

### Questions I Still Have

- ✅ How does temperature control randomness? → Answered: it reshapes the probability distribution before sampling — low temp concentrates mass on top tokens, high temp flattens it.
- How exactly are embeddings stored and queried in a vector DB? (cosine similarity search mechanics)
- What happens internally when the context window is exceeded — does the model truncate from the start, middle, or use a sliding window?

### Day 1 Reflection

**What felt clear?**

The token → number → neural network → prediction pipeline. The attention mechanism analogy ("which earlier word matters most right now") was very clear.

**What felt confusing?**

Temperature not yet covered at the time. Embeddings conceptually clear but storage in vector DB still fuzzy.

**What should I review tomorrow?**

- Temperature and how it affects output variability ✅ done in Day 2
- How embeddings are generated via API ✅ done in Day 2
- Context window limits for main models (GPT-4, Claude, Llama) — still to verify exact numbers

**Day 1 Status:** ✅ Complete

## Day 2 - Temperature, Deeper Context Window, Deeper Embeddings, LLMs Strengths and Weaknesses

**Date:** May 5, 2026

### What Was Learned

- Temperature: full understanding of probability distribution shaping, practical ranges, and when to use what value.
- Context window (deep): the whiteboard mental model, RAG as the solution to stuffing, attention degradation for distant tokens, real model size comparisons.
- Embeddings (deep): vector dimensions, cosine similarity, the famous `king - man + woman ≈ queen` relationship, the full RAG pipeline from chunk → embed → store → retrieve → generate.
- LLMs good at: expanded to 10 clear categories with examples.
- LLMs bad at: expanded with the production fix pattern (LLM + tools + memory + retrieval).

### Day 2 Checklist

- [x] Understand temperature fully.
- [x] Deepen context window understanding.
- [x] Deepen embeddings understanding.
- [x] Map out 10 LLM strength categories.
- [x] Map out LLM weakness categories with fixes.

### Day 2 Reflection

**What felt clear?**

Temperature clicked immediately once framed as "probability distribution shaping not knowledge changing." The RAG pipeline as the answer to context window limitations was a strong insight.

**What is still fuzzy?**

- Exact mechanics of cosine similarity search in a vector DB.
- What happens internally when context is exceeded (truncation strategy).

**Day 2 Status:** ✅ Complete

## Day 3 - Knowledge Test and Corrections

**Date:** May 5, 2026

### What Happened

Instead of jumping to API calls, I took a 16-question knowledge test covering everything from Day 1 and Day 2. The test exposed real gaps — things I thought I understood but was actually mixing up or had fundamentally wrong.

### Test Score Breakdown

| Area | Score | Notes |
| --- | --- | --- |
| Tokens | ✅ Strong | Solid on what they are, why they matter, code tokenization |
| Context window | ✅ Strong | Clear on limits, overflow, attention degradation |
| Temperature | ✅ Strong | Probability distribution shaping, practical ranges |
| Internal pipeline | ⚠️ Partial | Was mixing embedding stage with prediction stage |
| Embeddings | ⚠️ Partial | Kept confusing embeddings with token prediction |
| RAG | ❌ Wrong | Thought it was about privacy — it is about retrieval efficiency |
| Search vs LLM | ⚠️ Weak | Did not separate retrieval from generation |
| Why LLMs seem intelligent | ⚠️ Shallow | Said "lots of data" — missed pattern learning and emergence |

**Overall:** ~55-60%. Good on basics, major gaps on embeddings role, RAG, and search vs generation.

### Gaps Identified and Corrected

1. **Internal LLM pipeline** — clear separation: tokens → embeddings → transformer + attention → probability distribution → sampling
2. **Embeddings are representation, not prediction** — they convert tokens to meaning vectors, the transformer does the actual processing
3. **Two uses of embeddings** — inside LLM (internal layer) vs for RAG/search (embedding model API)
4. **RAG corrected** — NOT about privacy. It is about retrieval efficiency: retraining is expensive, RAG retrieves relevant chunks dynamically
5. **RAG pipeline** — docs → chunk → embed → vector DB → query embed → similarity search → retrieve → send to LLM → answer
6. **Search vs LLM** — search RETRIEVES existing info, LLM GENERATES new text. Modern AI combines both
7. **Why LLMs seem intelligent** — language contains reasoning patterns, prediction at scale learns structure, transformers learn relationships, emergence at scale
8. **Code tokenization** — code uses more tokens because symbols, brackets, operators all get split into individual tokens
9. **Cosine similarity** — measures angle between vectors for meaning comparison, powers vector database search

### Day 3 Reflection

**What the test proved I know well:**
Token mechanics, context window behavior, temperature control. These are solid.

**What the test exposed:**
I was treating the LLM pipeline as a blur — "text goes in, answer comes out." The test forced me to separate the stages and understand what each one does.

The RAG gap was the biggest. I had a completely wrong mental model (privacy/local hosting) when it is actually about retrieval efficiency and avoiding expensive retraining.

**Lesson learned:**
Testing yourself before moving on catches gaps that self-study hides. I thought I was ready for API calls, but I needed these corrections first.

**Day 3 Status:** ✅ Complete

## Day 4 - First LLM Interaction via Playground

**Date:** May 6, 2026

### What Happened

Instead of setting up local code and API keys, I used Google's AI Studio web playground to interact with the Gemini model directly. This was a great way to achieve the day's goal (make a first API call) without any friction.

### The Experiment

- **Tool:** Google AI Studio
- **Model:** Gemini
- **Prompt:** "explain goroutine simply"
- **Experiment:** Run the same prompt multiple times with different temperature settings to observe the variability in the model's responses.

### Key Learnings

1.  **LLMs are not deterministic:** The same prompt produced three different, high-quality answers. This is a core feature. The model explores different probable paths in its predictions.
2.  **Temperature drives variability:** The differences in the responses (new analogies like "Chef" vs. "Office Interns", different phrasing) are a direct result of temperature.
3.  **Playgrounds are powerful learning tools:** You can learn a huge amount about LLM behavior (prompting, system instructions, parameters) without writing a single line of code.
4.  **Models are excellent explainers:** The AI provided simple, accurate explanations of a complex programming concept, complete with analogies and code examples. This is a primary strength.
5.  **Grounding provides sources:** The `[1][2][3]` annotations in the responses show the model using "grounding" — checking its generated text against Google Search to provide sources and improve factuality.

### Day 4 Reflection

This was a smart shortcut. The goal was to understand the input/output behavior of a real model, and the playground was the fastest way to do that. I now have a concrete feel for how temperature affects output and how a model can be a powerful explanatory tool.

**Day 4 Status:** ✅ Complete

## Day 5 - Inference, Local Models, API Lifecycle, AI Engineer Stack

**Date:** May 7–12, 2026

### What Happened

Deep reading session over several days. Tried to get the Gemini API working via code but hit issues. Shifted to studying the full picture of how AI applications actually work — inference pipelines, local vs cloud models, the API lifecycle, what parameters control, and what the practical AI engineering stack looks like.

### Key Concepts Learned

1. **Inference** — using a trained model to generate output. Not training. Every API call = inference.
2. **LLMs are stateless** — no memory between requests. Chat apps re-send the entire conversation history every time. "Memory" is an app-level feature, not a model feature.
3. **System prompts** — behavior-shaping instructions sent before the user's message. They define personality, output format, and constraints.
4. **API parameters** — temperature, max_tokens, model selection, streaming. Each one is a control lever.
5. **Local inference (Ollama)** — run models on your own machine. Free, private, but limited by hardware. Good for learning.
6. **Model parameters** — what "7B" means. More parameters = smarter but slower and heavier. Phi-3 Mini (3.8B) is enough for learning.
7. **AI engineer vs ML researcher** — build products with AI (engineer) vs build new models (researcher). The engineer path is the high-leverage move.
8. **The build path** — chatbot → semantic search → mini RAG → knowledge assistant. Each phase makes the next one obvious.
9. **What NOT to learn yet** — LangChain, agents, fine-tuning, multi-agent systems. Build the fundamentals first.

### Day 5 Reflection

This was a theory-heavy period but important. The biggest insight: LLMs being stateless changes everything about how AI apps are designed. Chat history management, context window budgeting, and token cost control are all engineering problems that the app developer handles — the model just predicts tokens.

Ready to move from reading to building. Next: actually write code that calls an LLM.

**Day 5 Status:** ✅ Complete
