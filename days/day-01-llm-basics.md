# Day 01: What Is an LLM and How Does It Work

> An LLM is a giant neural network trained on huge amounts of text to predict the next piece of language so well that it can simulate conversation, coding, reasoning, and knowledge.

## What Is an LLM

LLM stands for **Large Language Model**. Examples: ChatGPT (OpenAI), Claude (Anthropic), Gemini (Google), Llama (Meta).

At the core, an LLM does one deceptively simple thing:

**Given some text, predict what token comes next.**

A "token" is usually a word piece. Example:

```
I want to drink hot ____
```

The model might predict: tea, coffee, chocolate.

Now imagine doing this billions of times across books, code, conversations, research papers, Stack Overflow, and documentation. Eventually the model starts learning grammar, reasoning patterns, coding structures, conversation style, facts, and even emotional tone.

It is basically compressing patterns of human language into math.

## The Training Pipeline

```
Internet + Books + Code + Data
            ↓
Convert words → numbers (tokens)
            ↓
Train giant neural network
            ↓
Adjust billions of parameters
            ↓
Model becomes good at predicting text
```

Those "parameters" are like tiny adjustable knobs. Modern LLMs have billions or even trillions of them.

## Why "Large"

- Massive training data
- Massive neural network
- Massive compute (thousands of GPUs)

## What Happens When You Send a Prompt

You say: `Write a Java function for BFS`

The model:
1. Converts text into tokens.
2. Converts tokens into vectors (embeddings).
3. Runs them through neural network layers.
4. Uses the **attention mechanism** to decide which earlier words matter most right now.
5. Predicts next token. Repeats until done.

## The Attention Mechanism

The "T" in GPT stands for **Transformer**. Transformers changed everything because of attention.

Attention lets the model decide: *"Which earlier words matter most right now?"*

Example:

```
The animal didn't cross the street because IT was too tired.
```

Attention helps understand: "it" = animal (not street).

This ability made modern LLMs explode in capability.

## Why LLMs Feel Intelligent

Intelligence in conversation is often: predicting useful responses, connecting concepts, simulating reasoning patterns.

The model is not "thinking" like humans do. It is more like an absurdly advanced autocomplete system trained on humanity's text. But once autocomplete becomes powerful enough, it starts looking like reasoning.

## Your Brain vs LLM

| Human Brain | LLM |
| --- | --- |
| Learns from experience | Learns from training data |
| Has emotions | No emotions |
| Understands physical world directly | Only through text/images |
| Thinks continuously | Generates token-by-token |
| Has goals/desires | No intrinsic goals |
| Energy efficient | GPU furnace |

## The Important Thing Most Beginners Miss

LLMs are not databases. They are **probabilistic pattern learners**.

Which means they can:
- Hallucinate (make stuff up)
- Forget details
- Make confident mistakes
- Reason surprisingly well
- Fail hilariously on simple things

---

## Tokens: The Basic Unit LLMs Process

Humans see: `"Hello world"`

The model sees something like: `[15496, 995]`

Those numbers are **tokens**.

### What Is a Token

A token is usually a word, part of a word, punctuation, spaces, or code symbols.

| Text | Possible Tokens |
| --- | --- |
| `hello` | `["hello"]` |
| `unbelievable` | `["un", "believ", "able"]` |
| `ChatGPT is cool` | `["Chat", "G", "PT", " is", " cool"]` |
| `console.log()` | `["console", ".", "log", "()"]` |

### Why Not Just Use Whole Words

Because language is chaos. There are millions of words, typos, slang, emojis, code, mixed languages, and new terms every day.

If models stored every full word separately, the vocabulary would explode and unknown words would break things.

Tokenization solves this by breaking text into reusable pieces — like LEGO blocks for language.

```
"playing" → ["play", "ing"]
```

Then the model already understands: play, player, replay, playing.

### Tokens Are NOT Equal to Words

Rough approximation: **1 token ≈ 0.75 English words**.

| Sentence | Approx Tokens |
| --- | --- |
| "Hi" | 1 |
| "How are you?" | 4 |
| Large paragraph | 100+ |

Code usually consumes more tokens because symbols get split aggressively.

### Why Tokens Matter

LLM pricing and limits are token-based.

- **Input tokens** = what you send
- **Output tokens** = what model generates
- You pay for both

```
Huge prompt + huge response = expensive
```

### Token Prediction Example

Input: `I love drinking hot`

Model predicts probabilities:

| Token | Probability |
| --- | --- |
| coffee | 45% |
| tea | 35% |
| soup | 5% |
| lava | 0.0001% |

Then it picks one. Repeat thousands of times. That is text generation.

---

## Key Takeaways

- An LLM predicts the next token given all previous tokens — billions of times.
- Tokens are word-pieces, not words. 1 token ≈ 0.75 words.
- Pricing, speed, and memory limits are all token-based.
- The Transformer architecture and attention mechanism are what made modern LLMs possible.
- LLMs are pattern predictors, not databases — they can hallucinate.

## One-Line Summaries

**LLM:** A giant neural network trained on text to predict the next token so well that it simulates conversation, coding, and reasoning.

**Token:** A small chunk of text that an LLM converts language into so it can process, understand, and predict text mathematically.

---

> **Post-test note:** After a knowledge test on Day 03, I realised I hadn't fully internalised the pipeline stages and was mixing embeddings with token prediction. See [day-03-corrections-and-gaps.md](day-03-corrections-and-gaps.md) for the corrected mental model.

---

## Revision Questions

Test yourself. Cover the answers and try to explain each one before looking.

1. **What does an LLM actually do at its core?** *(Hint: it is one simple operation repeated billions of times)*
2. **What is a token? Why doesn't the model just use whole words?**
3. **Roughly how many tokens equal one English word? Why does code use more tokens?**
4. **List the 5 steps that happen when you send a prompt to an LLM.** *(tokenize → ? → ? → ? → ?)*
5. **What is the attention mechanism and why was it a breakthrough?**
6. **Why do LLMs "feel" intelligent even though they are just predicting the next token?**
7. **Name 3 things LLMs can do surprisingly well, and 3 things they fail at.**
8. **What does "probabilistic pattern learner" mean? Why is this different from a database?**
9. **If an LLM says something wrong with full confidence, what is that called? Why does it happen?**
10. **You send a 500-word prompt. Roughly how many tokens is that? How does that affect cost?**
