# AI Learning Progress Log

Started: April 30, 2026

Use this file as the day-to-day working journal for the AI roadmap. Keep the main roadmap stable, and update this file with what you actually did, learned, struggled with, and will do next.

## Current Focus

**Phase:** Month 1 - Foundation And First AI Tool  
**Current Day:** Day 2  
**Main Goal:** Make a first LLM API call.

## Progress Summary

| Area | Status |
| --- | --- |
| LLM basics | ✅ Complete |
| Tokens | ✅ Complete |
| Context window | ✅ Complete |
| Temperature | 🔲 Pending |
| Embeddings (overview) | ✅ Complete |
| Notes written | ✅ Complete |
| Concepts explained in own words | ✅ Complete |
| Day 1 reflection | ✅ Complete |

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
- [ ] Explain temperature in your own words. _(next)_
- [x] Explain embeddings in your own words.
- [x] Write 3 examples of tasks LLMs are good at.
- [x] Write 3 examples of tasks LLMs are weak or risky at.
- [ ] Write one question you still have.
- [x] Mark Day 1 complete.

### Notes

- An LLM is a giant neural network trained on text data to predict the next token — repeat that billions of times and you get something that looks like reasoning.
- The "T" in GPT stands for Transformer. The Attention mechanism inside Transformers lets the model decide which earlier words matter most when generating the next one.
- Training pipeline: raw text → tokenize → convert to vectors → train neural network → adjust billions of parameters → model that predicts text well.
- LLMs are called "large" because of massive training data, massive model size, and massive compute (thousands of GPUs).
- A token is usually a word, part of a word, punctuation, or code symbol. `unbelievable` → `["un", "believ", "able"]`.
- Rough rule: 1 token ≈ 0.75 English words. Code tends to use more tokens because symbols get split aggressively.
- LLM pricing is token-based: input tokens + output tokens = cost. A badly optimised prompt is a money leak.
- Context window = how many tokens the model can "see" at once (its working memory). If you exceed it, old content gets dropped.
- Embeddings convert tokens into vectors (lists of numbers). Similar meaning → similar vectors. This is what makes semantic search and RAG possible.
- LLMs are probabilistic, not deterministic. They pick from a probability distribution each token — that is why the same prompt can give different outputs.

### Concepts In My Own Words

#### What is an LLM?

A Large Language Model is a neural network trained on enormous amounts of text. Its one core job is to predict the next token given all previous tokens. Do that billions of times across books, code, and conversations, and the model ends up compressing human language patterns into math. It looks like reasoning because good enough prediction eventually simulates reasoning. It is not "thinking" — it is an absurdly advanced autocomplete trained on humanity's text.

#### What are tokens?

A token is the basic unit an LLM processes. Not exactly a word — more like a word-piece. The tokenizer splits text into chunks the model can work with as numbers. `"ChatGPT is cool"` might become `["Chat", "G", "PT", " is", " cool"]`. This matters because pricing, speed, and the context window are all measured in tokens, not words. 1 token ≈ 0.75 English words.

#### What is a context window?

The context window is the total number of tokens the model can hold in memory at once — both input and output combined. Think of it as RAM for the conversation. If you send a huge document plus a long conversation history, once you hit the limit the model starts dropping earlier content. That is why AI sometimes seems to forget what you said earlier.

#### What is temperature?

_(Not yet learned — Day 2 or Day 3 topic)_

#### What are embeddings?

Embeddings are numerical representations of text — lists of floating-point numbers (vectors). The key property: text with similar meaning gets similar vectors. This is what makes semantic search possible: instead of matching exact words, you find text that is close in meaning. Embeddings are also the foundation of RAG (Retrieval-Augmented Generation), where relevant documents are found by vector similarity before being passed to the model.


### LLMs Are Good At

- Generating code, writing, and structured text (JSON, markdown, summaries)
- Simulating reasoning, connecting concepts, and explaining things
- Following instructions, translating, reformatting, and classifying text

### LLMs Are Weak Or Risky At

- Hallucinating — stating wrong facts confidently
- Precise arithmetic and counting
- Tasks requiring up-to-date or private knowledge (without RAG or tools)

### Question I Still Have

- How exactly does temperature control randomness at the math level? (probability distribution shaping — look this up next)

### Day 1 Reflection

**What felt clear?**

The token → number → neural network → prediction pipeline. The attention mechanism analogy ("which earlier word matters most right now") was very clear.

**What felt confusing?**

Temperature not yet covered. Embeddings are conceptually clear but how they are generated and stored in a vector DB is still fuzzy.

**What should I review tomorrow?**

- Temperature and how it affects output variability
- How embeddings are generated via the API (one API call returns a vector)
- Context window limits for the main models (GPT-4, Claude, Llama)

**Day 1 Status:** ✅ Complete

## Day 2 Preview

Goal: Make your first LLM API call.

Planned tasks:

- [ ] Choose OpenAI or Anthropic for the first API experiment.
- [ ] Create or confirm API key access.
- [ ] Set up a tiny Node.js or Python script.
- [ ] Send one prompt.
- [ ] Print the response.

## Weekly Review Template

Use this every 7 days.

### Week Of


### What I Completed

- 

### What I Built

- 

### What I Learned

- 

### What Was Hard

- 

### What I Will Do Next Week

- 
