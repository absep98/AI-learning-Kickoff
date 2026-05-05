# Day 02: Temperature, Context Window (Deep), Embeddings (Deep), LLM Strengths and Weaknesses

---

## Context Window

The context window is the AI's **short-term working memory** — the amount of text/tokens the model can "see" at one time while generating a response.

### The Whiteboard Analogy

Imagine solving a coding problem on a whiteboard with limited space. As new stuff gets written, old stuff gets erased. That whiteboard size = context window.

### What Fits Inside

Everything counts:
- Your messages
- Previous chat history
- Uploaded text
- System instructions
- Model replies

ALL must fit inside the token limit.

Example: an 8K context window means all of the above must fit in ~8000 tokens. If conversation becomes too long, older messages disappear from memory.

### Real Example

You say at the start: `My favorite language is Go`

200 messages later: `Which language do I like?`

If the earlier message got pushed out of context:

```
AI: "I'm not sure."
```

Not because it "forgot" emotionally — the text literally no longer exists in its active memory window.

### Context Window Sizes

| Size | What It Can Handle |
| --- | --- |
| 8k | Short conversations |
| 32k | Moderate documents |
| 128k | Large codebases, books |
| 1M+ | Entire fantasy trilogies + the database schema |

Bigger context = more memory but also more expensive and slower.

### The Subtle Thing

The model does not "understand" all context equally. Usually:
- Recent tokens matter more.
- Relevant tokens get attention.
- Old details may weaken.

Even if technically inside the window, stuffing 500 pages blindly creates **information soup**.

### Why RAG Exists

RAG (Retrieval Augmented Generation) exists because of context window limitations.

Instead of stuffing everything into the context:
1. Store docs in a database.
2. Retrieve only relevant chunks.
3. Send those chunks to the LLM.

Like giving a chef ingredients instead of dumping the whole supermarket into the pan.

### Attention Cost

Internally, every token attends to every other token. Attention computation grows heavily with context size. That is why huge context windows are computationally expensive.

---

## Temperature

Temperature controls how **predictable vs creative** the AI becomes. It changes how the model chooses the next token from its probability list.

### How It Works

Model predicts probabilities for the next token:

| Token | Probability |
| --- | --- |
| coffee | 50% |
| tea | 30% |
| lava | 0.01% |

Temperature changes how "safe" or "wild" the selection becomes.

### Low Temperature = Conservative

```
temperature = 0.1
```

Model picks the statistically safest option. Result: stable, deterministic, repetitive, factual.

Usually picks: `coffee`

Great for: coding, math, structured outputs, APIs, debugging.

### High Temperature = Creative

```
temperature = 1.2
```

Probabilities flatten. Less obvious tokens become viable.

Might pick: `lava`

Great for: storytelling, brainstorming, creative writing.

Bad for: production SQL queries.

### Visual Intuition

```
Low temperature:  [90%, 5%, 3%, 2%]
High temperature: [40%, 25%, 20%, 15%]
```

Higher temperature spreads probability more evenly across options.

### The Key Insight

Temperature does NOT add knowledge. It only changes how adventurous token selection becomes.

Same brain. Different caffeine level.

### Practical Guide

| Use Case | Temperature |
| --- | --- |
| Coding assistant | 0.1–0.3 |
| Customer support | 0.3–0.5 |
| General chatbot | 0.7 |
| Creative writing | 0.9–1.2 |

### API Example

```json
{
  "temperature": 0.2
}
```

### Edge Case

Even with `temperature = 0`, some systems may not be perfectly deterministic because of hardware parallelism and backend optimisations. But it becomes much more stable.

---

## Embeddings (Deep Dive)

Embeddings are how AI turns **meaning into coordinates** in mathematical space.

> An embedding is a list of numbers representing the meaning of something.

### How It Looks

```
"king"  → [0.21, -0.44, 1.92, ...]
"queen" → [0.19, -0.40, 1.88, ...]
```

Those numbers look random but they encode semantic meaning. **Similar meanings end up near each other in vector space.**

### Semantic Relationships

In vector space:
```
dog  ≈ puppy
cat  ≈ kitten
Java ≈ Spring Boot
```

Things with related meanings cluster together.

### The Famous Example

```
King - Man + Woman ≈ Queen
```

The math actually worked. The vectors encode semantic structure that arithmetic can manipulate.

### Why Embeddings Matter

They power:
- Semantic search (meaning-based, not keyword-based)
- RAG systems
- Recommendation systems
- Similarity matching
- Memory retrieval
- Clustering

Embeddings are the "understanding layer" of modern AI systems.

### Semantic Search Example

Without embeddings, searching for `"car"` will NOT find `"automobile"` because exact words differ.

With embeddings, both meanings are close in vector space. Search becomes **meaning-based instead of keyword-based**.

### How RAG Uses Embeddings

1. Split documents into chunks.
2. Convert each chunk into an embedding (one API call).
3. Store embeddings in a vector database.
4. User asks a question → question becomes an embedding.
5. Find closest matching chunk embeddings (cosine similarity).
6. Send those chunks to the LLM as context.

Result: private company chatbot without retraining the model.

### Embeddings Are Not Human-Readable

Humans see: `"machine learning"`

Model sees: `[-0.221, 0.991, 1.337, ...]`

Usually hundreds or thousands of dimensions: 384, 768, or 1536.

### Important Distinction

| Thing | Purpose |
| --- | --- |
| Tokens | Break text into processable chunks |
| Embeddings | Represent meaning numerically |
| LLM | Predict next tokens |

These are connected but different layers.

---

## What LLMs Are Good At

### 1. Language and Conversation
Explaining, summarising, translating, rewriting, tutoring, brainstorming. This is their home turf.

### 2. Coding
Boilerplate generation, debugging, explaining code, API usage, refactoring, test generation, SQL queries, regex. Tools like GitHub Copilot exist because of this.

### 3. Pattern Recognition
Spotting structure, repetition, relationships, and intent from examples without explicit rules.

### 4. Summarisation
Compressing PDFs, meetings, logs, emails, and research papers into bullet points.

### 5. Text Transformation
Converting formats and styles: formal → casual, notes → blog, English → Hindi, code → explanation.

### 6. Knowledge Retrieval (Sort Of)
LLMs remember lots of facts from training. But they are NOT guaranteed accurate — not databases. Sometimes 95% genius, 5% confident nonsense.

### 7. Reasoning-Style Tasks
Breaking down problems, step-by-step analysis. Especially when prompted with "Think step by step."

### 8. Generating Synthetic Data
Mock APIs, fake datasets, test cases, placeholder content.

### 9. Semantic Understanding
Meaning matching, semantic search, document retrieval, recommendations via embeddings + transformers.

### 10. Learning Acceleration
LLMs reduce friction between "I want to build X" and "I shipped X." Especially for solo developers, startups, and learners.

---

## What LLMs Are Bad At

- **Guaranteed factual accuracy** — they are pattern predictors, not databases.
- **Exact arithmetic** — a calculator crushes an LLM on `187463 × 92827`.
- **Long-term planning** — no persistent memory across sessions without explicit systems.
- **True understanding** — simulating reasoning ≠ understanding.
- **Real-world grounding** — only knows the world through text and images.
- **Reliability under ambiguity** — vague prompts produce wildly inconsistent results.

### The Fix Pattern

The strongest AI systems are not "LLM alone." They are:

```
LLM + tools + memory + retrieval + execution
```

That is where the real production systems emerge.

---

## Key Takeaways

- Context window = whiteboard. Everything must fit. When full, old stuff drops. That is why RAG exists.
- Temperature = probability distribution shaping, not knowledge changing. Low for code, high for creativity.
- Embeddings = meaning as vectors. Similar meaning → close vectors. Powers semantic search and RAG.
- LLMs are spectacularly good at language-shaped tasks but need tools, retrieval, and memory for production reliability.

## One-Line Summaries

**Context window:** The maximum amount of text/tokens an LLM can actively consider at once while generating a response.

**Temperature:** Controls how random or creative an LLM's token selection becomes during text generation.

**Embeddings:** Numerical vector representations that allow AI systems to understand and compare the meaning of text, code, images, or other data.
