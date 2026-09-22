# Learning AI in Public

A software engineer's day-by-day journey from zero AI knowledge to building real AI-powered applications.

No ML degree. No 3-month course first. Just learn one concept, build something, ship it, repeat.

## Who Is This For

- Software engineers who want to stay relevant as AI changes the industry.
- Beginners who want a practical, build-first approach instead of academic theory.
- Anyone who learns better by reading someone's real notes instead of polished tutorials.

## How This Repo Works

I learn something every day, write it up in plain language, and commit it here. The notes are raw, honest, and written to be understood by someone with zero AI background.

### Start Here

| What | Where | Purpose |
| --- | --- | --- |
| **Daily notes** | [`days/`](days/) | The actual learning content. Start with Day 01. |
| **6-month roadmap** | [`roadmap.md`](roadmap.md) | The full plan: what to learn, in what order, with projects. |
| **My progress** | [`progress.md`](progress.md) | Personal tracker. See what I've done and what's next. |
| **Cheat sheet** | [`cheatsheet.md`](cheatsheet.md) | Master glossary and quick-reference for all concepts. |
| **Projects** | [`projects/`](projects/) | Code projects built during the journey. |

## Quick Navigation

### Month 1: Foundation And First AI Tool

| Day | Topic | Key Concepts |
| --- | --- | --- |
| [Day 01](days/day-01-llm-basics.md) | LLM Basics | What is an LLM, tokens, how text becomes numbers |
| [Day 02](days/day-02-temperature-context-embeddings.md) | Temperature, Context Window, Embeddings | Probability shaping, working memory, meaning as vectors, what LLMs are good/bad at |
| [Day 03](days/day-03-corrections-and-gaps.md) | Knowledge Test + Corrections | Test results, pipeline fix, RAG corrected, search vs LLM, embeddings clarified |
| [Day 04](days/day-04-api-playground.md) | First API Call (Playground) | Model variability, temperature effects, using web playgrounds for learning |
| [Day 05](days/day-05-inference-local-models-api-lifecycle.md) | Inference, Local Models, API Lifecycle | Statelessness, system prompts, API params, local vs cloud, model sizes, AI engineer stack |
| [Day 06](days/day-06-hands-on-ollama-experiments.md) | Hands-On Ollama Experiments | Local inference observed, memory proved fake, small model limits, prompt sensitivity, compound AI systems |
| [Day 07](days/day-07-pipeline-hands-on.md) | Pipeline Made Real | Tokenization with tiktoken, embeddings with all-minilm, cosine similarity proved, chat vs embedding models |
| [Day 08](days/day-08-terminal-chatbot.md) | Terminal Chatbot | Built a streaming chatbot with Ollama, statelessness solved, system prompts, 4-step chat loop |
| [Day 09](days/day-09-semantic-search.md) | Semantic Search | Embedding-based retrieval, cosine ranking, pooling concept, same-model rule, the retrieval half of RAG |
| [Day 10](days/day-10-rag.md) | RAG | Combined semantic search + chatbot, context injection, two-model architecture, grounded answers from documents |
| [Day 11](days/day-11-rag-over-notes.md) | RAG Over Real Notes | Chunking strategy, filtering, 467 chunks from real notes, retrieval quality debugging |
| [Day 12](days/day-12-rag-improved.md) | RAG Improved | Persistent cache, source tracking, deduplication, score threshold, retrieval vs generation debugging |
| [Day 13](days/day-13-structured-output.md) | Structured JSON Output | System prompt format control, stream:false, JSON parsing, format compliance, computed confidence |
| [Day 14](days/day-14-chromadb.md) | ChromaDB Vector Database | PersistentClient, collection, HNSW index, cosine distance, JSON file replaced |
| [Day 15](days/day-15-cloud-api.md) | Cloud API (Groq + Llama) | Replaced local phi3:mini with Groq, API key management, retrieval vs generation independence |
| [Day 16](days/day-16-rag-evals.md) | RAG Evals | Automated testing with 20 questions, answer/source validation, 5% baseline established, system gaps exposed |
| [Day 17](days/day-17-git-ai-summary.md) | git-ai-summary CLI | Git diff summarizer, Groq JSON output, unstaged/staged/both modes, robust error handling |
| [Day 18](days/day-18-workflow-topics.md) | Workflow Topics | Memory strategy, tool-calling loop rules, runnable mock loop prototype |
| [Day 19](days/day-19-real-planner-tool-integration.md) | Real Planner + Tool Integration | Real Groq planner, real tool executor, allowed-action guardrails |
| [Day 20](days/day-20-decision-metadata-tools.md) | Decision Metadata + Tools | check_git_status tool, planner_source and retry_attempts log metadata |
| [Day 21](days/day-21-persist-step-logs.md) | Persist Step Logs | Step logs written to timestamped JSON files after each run |
| [Day 22](days/day-22-planner-conversation-history.md) | Planner Conversation History | Prior steps replayed as chat history so the planner has memory across a run |
| [Day 23](days/day-23-hardening-workflow-loop.md) | Hardening The Workflow Loop | Natural-language final response, retry-failure visibility, early stop on repeated clarification |
| [Day 24](days/day-24-repo-assistant.md) | Repo Assistant: RAG + Tool Routing | Separated retrieval from generation, combined RAG with tool routing into one working assistant |
| [Day 25](days/day-25-model-based-planner.md) | Model-Based Planner For Repo Assistant | Keyword router replaced with a model-based planner, validated fallback safety |
| [Day 26](days/day-26-read-progress-files-tool.md) | Third Tool: read_progress_files | Fixed a real RAG hallucination bug by adding a dedicated tool instead of trusting retrieval |
| [Day 27](days/day-27-fastapi-wrapper.md) | Wrapping Repo Assistant In A FastAPI Web API | FastAPI fundamentals, ported CLI logic to a POST /ask endpoint, env-var-configurable paths |

*(This table grows as I progress. Days 23-27 notes were drafted retroactively from actual commits/tests and reviewed before being added here.)*

**Days 28+:** in progress — see [`progress.md`](progress.md) for current status (remaining blocker: local Ollama dependency needs solving before real deployment).

## The Learning Approach

```
1. Learn one concept.
2. Write it in your own words.
3. Build something small with it.
4. Test it.
5. Write down what worked and what failed.
6. Commit and push.
```

No frameworks before fundamentals. No courses before building. No theory without practice.

## Tech Stack

- **Languages:** Node.js / Python (whichever fits the task)
- **LLM APIs:** OpenAI, Anthropic (Claude)
- **Tools:** VS Code, Cursor, GitHub Copilot
- **Vector DBs:** TBD (Supabase pgvector, Chroma, or Qdrant)

## How To Use This Repo As A Beginner

1. Read [`roadmap.md`](roadmap.md) to understand the full plan.
2. Go to [`days/`](days/) and start reading from Day 01.
3. Each day's file is self-contained — you can read it without context.
4. When projects start appearing in [`projects/`](projects/), clone and try them yourself.
5. If something is unclear, open an issue — I'll try to improve the explanation.

## About Me

Software engineer learning AI to stay relevant, build useful products, and share the journey publicly. One day at a time.

---

*This is a living repo. Updated daily (or close to it).*
