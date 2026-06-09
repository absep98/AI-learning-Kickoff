# AI Learning Roadmap for a Software Engineer

Created: April 30, 2026

## Why This Plan Exists

You are a software engineer and you are worried that AI will reduce traditional software jobs over the next 1-2 years. The best response is not to pause everything and become a machine learning researcher. The best response is to become an AI-native software engineer: someone who can use AI tools daily, build AI-powered features, evaluate quality, control cost and risk, and ship useful products.

Your goal is to stay relevant by combining strong software engineering with practical AI application engineering.

## Target Role

Aim for this profile:

**AI-native Software Engineer / AI Product Engineer**

This means you can:

- Build normal production software: frontend, backend, APIs, auth, databases, jobs, payments, deployment.
- Use AI coding tools to move faster without losing engineering judgment.
- Integrate LLM APIs into real products.
- Build RAG systems over private data.
- Build tool-using workflows and controlled agents.
- Evaluate AI output with tests, traces, and user feedback.
- Handle cost, latency, hallucinations, privacy, and prompt injection.
- Explain trade-offs clearly in interviews or product discussions.

## Guiding Principle

Learn AI by building useful things, not by collecting courses.

Use this loop:

1. Learn one concept.
2. Build a tiny feature with it.
3. Test it.
4. Write down what worked and failed.
5. Improve it.
6. Ship or publish the result.

## What To Learn In Order

### 1. AI-Assisted Development

Purpose: use AI to become faster at your existing software work.

Learn:

- How to ask AI for implementation options.
- How to use AI for debugging.
- How to ask AI to review your diff.
- How to generate focused tests.
- How to verify AI-generated code instead of blindly trusting it.

Daily practice:

- Use Copilot, Cursor, Claude, ChatGPT, or similar tools while coding.
- Ask AI to explain unfamiliar code.
- Ask AI for edge cases before you implement.
- Ask AI to create test cases after you implement.
- Ask AI to review your code before you open a PR.

Success signal:

- You can complete routine tasks faster while still understanding every line that ships.

### 2. LLM Application Basics

Purpose: understand how LLM APIs behave in real applications.

Learn:

- Tokens
- Context windows
- Temperature
- Model selection
- Structured JSON output
- Streaming responses
- Rate limits
- Retries
- API errors
- Cost tracking
- Prompt versioning
- Secrets management

Build:

- A small CLI tool that calls an LLM API and returns structured output.

Success signal:

- You can build a simple AI feature without a framework.

### 3. Prompt Engineering With Evals

Purpose: stop treating prompts as magic text and start treating them as product logic.

Learn:

- System/developer instructions
- User inputs
- Few-shot examples
- Output schemas
- Prompt chaining
- Prompt regression tests
- Success criteria
- Failure cases

Build:

- A prompt test file with 10-20 real examples.
- A script that runs the prompt against those examples.
- A simple pass/fail review process.

Success signal:

- You can improve a prompt without relying only on vibes.

### 4. RAG: Retrieval-Augmented Generation

Purpose: build AI features that answer questions using private or product-specific data.

Learn:

- Embeddings
- Chunking
- Vector search
- Hybrid search
- Reranking
- Source citations
- Document parsing
- Retrieval evaluation
- Hallucination control

Build:

- ✅ Toy RAG with hardcoded documents (Day 10)
- **RAG over real files** — read `days/*.md`, chunk by paragraph, embed chunks, search your own notes (Day 11)
- Chat with project docs.
- Chat with PDFs.
- Internal knowledge-base assistant.

Success signal:

- Your system can answer questions using supplied documents and cite where the answer came from.

### 5. Tool Calling And Workflows

Purpose: let the model use functions/APIs safely.

Learn:

- Function/tool schemas
- Tool results
- Multi-step workflows
- Human approval
- Permission boundaries
- Tool-call logging
- Max step limits
- Recovery from failed tool calls

Build:

- GitHub issue assistant.
- Support-ticket assistant.
- Personal work assistant.
- Code review helper.

Success signal:

- The AI can take useful actions through your code while staying observable and controlled.

### 6. AI Product Engineering

Purpose: make AI features production-ready.

Learn:

- Logging and tracing
- Prompt/model evals
- Human review loops
- Cost monitoring
- Latency optimization
- Caching
- Privacy and PII handling
- Prompt injection defense
- User feedback loops
- Model fallback strategy

Success signal:

- You can explain not only how the AI feature works, but how you know it works.

## Six-Month Roadmap

## Month 1: Foundation And First AI Tool

Theme: learn by building your first small AI utility.

### Week 1

Tasks:

- [ ] Watch one beginner LLM intro.
- [ ] Learn tokens, context windows, temperature, embeddings at a high level.
- [ ] Read one LLM API quickstart: OpenAI or Anthropic.
- [ ] Make one basic API call from Node.js or Python.
- [ ] Make the model return structured JSON.

Recommended resources:

- Andrej Karpathy: Intro to Large Language Models
- Google Machine Learning Crash Course: Intro to LLMs
- OpenAI text generation docs
- Anthropic prompt engineering overview

### Week 2

Build project 1:

**git-ai-summary**

A CLI that summarizes git diffs or commits.

Features:

- [ ] Read a git diff or pasted diff.
- [ ] Generate summary.
- [ ] Generate risk list.
- [ ] Generate test suggestions.
- [ ] Return JSON output.
- [ ] Support streaming output.
- [ ] Handle API errors.
- [ ] Log estimated cost.

Example output:

```json
{
  "summary": "Adds payment webhook handling and subscription state updates.",
  "risks": ["Webhook replay handling may be missing"],
  "tests": ["Test duplicate webhook events", "Test failed payment transition"]
}
```

### Week 3

Improve the tool:

- [ ] Add 10 sample diffs.
- [ ] Write expected output qualities.
- [ ] Compare outputs manually.
- [ ] Improve the prompt.
- [ ] Track failures in a markdown table.

### Week 4

Package the learning:

- [ ] Write a README.
- [ ] Write a short case study.
- [ ] Record what worked and what failed.
- [ ] Add this project to your portfolio or private notes.

Month 1 outcome:

- You can call an LLM API directly.
- You understand structured outputs, retries, streaming, and cost basics.
- You have one useful AI developer tool.

## Month 2: AI Coding Workflow And A Product Feature

Theme: use AI in daily software engineering and add one practical AI feature.

Tasks:

- [ ] Use AI in your coding workflow every workday.
- [ ] Ask AI for implementation options before coding.
- [ ] Ask AI for test cases after coding.
- [ ] Ask AI to review your diff.
- [ ] Track where AI helped and where it failed.

Build project 2:

Add a simple AI feature to an app, extension, or small product.

Good feature ideas:

- AI summary
- AI categorization
- AI template generator
- AI bug explanation
- AI writing assistant
- AI support reply draft
- AI code comment explainer

Minimum requirements:

- [ ] One clear user problem.
- [ ] One LLM API call.
- [ ] Loading state.
- [ ] Error state.
- [ ] Retry behavior.
- [ ] Cost-safe prompt length limits.
- [ ] Basic tests.

Month 2 outcome:

- You are faster with AI-assisted development.
- You have shipped or built one actual AI product feature.

## Month 3: RAG Project

Theme: build AI over your own data.

Build project 3:

**Chat with project docs** or **Chat with PDFs**

Suggested stack:

- Frontend: React or Next.js
- Backend: Node.js/Express, Next.js API routes, or Python/FastAPI
- Vector store: Supabase pgvector, Chroma, Qdrant, or Postgres + pgvector
- LLM: OpenAI or Anthropic

Features:

- [ ] Upload or index documents.
- [ ] Split documents into chunks.
- [ ] Generate embeddings.
- [ ] Store embeddings.
- [ ] Retrieve relevant chunks for a question.
- [ ] Ask the LLM to answer using only retrieved context.
- [ ] Show source citations.
- [ ] Show when answer is unknown.
- [ ] Log retrieved chunks for debugging.

Important concepts:

- Bad answers often come from bad retrieval, not bad generation.
- Chunking strategy matters.
- Citations increase trust.
- The model should say "I do not know" when context is insufficient.

Month 3 outcome:

- You understand the most common enterprise AI pattern: AI over private data.

## Month 4: Evals And Production Quality

Theme: move beyond demos.

Add evals to your RAG project.

Tasks:

- [ ] Create 20 real questions.
- [ ] Define expected answers or expected source documents.
- [ ] Write an eval script.
- [ ] Track pass/fail manually at first.
- [ ] Categorize failures.
- [ ] Add traces for prompt, retrieved chunks, answer, latency, and cost.

Failure categories:

- Bad retrieval
- Missing source data
- Prompt issue
- Hallucination
- Formatting issue
- Tool/API failure
- User asked unsupported question

Add production concerns:

- [ ] API key safety.
- [ ] Rate limit handling.
- [ ] Request timeout.
- [ ] Input length limit.
- [ ] Cost logging.
- [ ] Basic prompt injection checks.
- [ ] User feedback: thumbs up/down or correction.

Month 4 outcome:

- You can prove whether an AI feature works.
- You can debug why it fails.
- This is a major differentiator in interviews.

## Month 5: Tool-Using Agent Or Workflow

Theme: build controlled automation.

Build project 4:

Choose one:

- GitHub issue assistant
- Support-ticket assistant
- Personal work assistant
- PR review helper
- Customer email assistant

The assistant should use tools such as:

- Search docs
- Read issue/ticket
- Classify priority
- Draft response
- Suggest next action
- Create checklist
- Search codebase

Safety requirements:

- [ ] Human approval before irreversible actions.
- [ ] Max step limit.
- [ ] Tool-call logs.
- [ ] Clear permission boundaries.
- [ ] Graceful failure when uncertain.
- [ ] No hidden autonomous behavior.

Example workflow:

1. User gives a GitHub issue.
2. AI classifies issue type.
3. AI searches docs/code.
4. AI proposes likely files to inspect.
5. AI drafts implementation plan.
6. Human approves.
7. AI generates checklist or draft patch.

Month 5 outcome:

- You understand practical agents as tool-using workflows, not magic autonomy.

## Month 6: Portfolio And Career Positioning

Theme: turn projects into career value.

Prepare 3 case studies:

### Case Study 1: AI Developer CLI

Explain:

- Problem solved
- Architecture
- Prompt design
- Structured output
- Error handling
- Cost handling
- What you learned

### Case Study 2: RAG App

Explain:

- Data ingestion
- Chunking strategy
- Embeddings
- Vector search
- Citations
- Evals
- Failure handling

### Case Study 3: Tool-Using Workflow

Explain:

- Tools available to the model
- Permission model
- Human approval points
- Logging
- Safety boundaries
- Where agents help and where normal code is better

Interview preparation questions:

- [ ] When would you use RAG vs fine-tuning?
- [ ] How do you reduce hallucinations?
- [ ] How do you evaluate an AI feature?
- [ ] How do you handle prompt injection?
- [ ] How do you control LLM API cost?
- [ ] How do you choose a model?
- [ ] How do you design human-in-the-loop workflows?
- [ ] How has AI changed your daily software workflow?

Month 6 outcome:

- You have practical AI projects.
- You can speak like someone who has built real AI features.
- You are positioned for AI-native SWE roles, internal AI initiatives, or indie products.

## Weekly Routine

Target: 7-10 hours per week.

Suggested split:

- 2 hours: focused learning
- 4 hours: building
- 1 hour: testing/evals
- 1 hour: notes/case study
- 1-2 hours: using AI in real work

Minimum viable week:

- 1 concept learned
- 1 small feature built
- 1 note written
- 1 failure captured

## Daily AI Practice Template

Use this when coding:

```md
## Task
What am I trying to build or fix?

## AI Used For
- [ ] Planning
- [ ] Code generation
- [ ] Debugging
- [ ] Test generation
- [ ] Code review
- [ ] Documentation

## What Worked

## What Failed

## What I Verified Myself

## Lesson
```

## Project Backlog

Use this list when you need project ideas.

Beginner:

- [ ] Git commit summarizer
- [ ] PR description generator
- [ ] Resume bullet improver
- [ ] Meeting notes summarizer
- [ ] Error message explainer
- [ ] Test case generator

Intermediate:

- [ ] Chat with docs
- [ ] Chat with PDFs
- [ ] Customer support draft assistant
- [ ] Codebase Q&A assistant
- [ ] AI changelog generator
- [ ] AI bug triage assistant

Advanced:

- [ ] Tool-using GitHub issue assistant
- [ ] PR review assistant with evals
- [ ] Multi-step research assistant
- [ ] AI workflow with human approval
- [ ] Internal knowledge assistant with access controls

## Resource List

Start here:

- Andrej Karpathy: Intro to Large Language Models
- Google Machine Learning Crash Course: LLM and embeddings modules
- OpenAI docs: text generation, structured outputs, embeddings, tool/function calling
- Anthropic docs: prompt engineering, tool use, building effective agents
- Hamel Husain: Your AI Product Needs Evals
- LlamaIndex docs: RAG and context augmentation
- LangChain/LangGraph docs: use after you understand direct API workflows

## What Not To Prioritize Yet

Avoid going too deep into these before you have built the first 3 projects:

- Training models from scratch
- Heavy ML math
- Fine-tuning
- Full LangChain course
- Multi-agent frameworks
- Local GPU hosting
- Research papers as the main learning path
- Kubernetes or advanced AI infrastructure

These are useful later, but they are not the best beginner path for a working software engineer.

## Skill Checklist

### LLM API Basics

- [ ] Make API call
- [ ] Stream response
- [ ] Return JSON
- [ ] Handle errors
- [ ] Handle retries
- [ ] Track cost
- [ ] Store prompts safely

### Prompting

- [ ] Write clear task prompts
- [ ] Use examples
- [ ] Use output schemas
- [ ] Separate system/developer/user instructions
- [ ] Create prompt test cases
- [ ] Track prompt versions

### RAG

- [ ] Parse documents
- [ ] Chunk documents
- [ ] Generate embeddings
- [ ] Store vectors
- [ ] Retrieve chunks
- [ ] Cite sources
- [ ] Evaluate retrieval quality

### Agents And Tool Use

- [ ] Define tool schema
- [ ] Execute tool calls
- [ ] Return tool results
- [ ] Log tool calls
- [ ] Add approval gates
- [ ] Add step limits
- [ ] Handle tool failure

### Production AI

- [ ] Add tracing
- [ ] Add evals
- [ ] Add cost limits
- [ ] Add rate limit handling
- [ ] Add privacy checks
- [ ] Add prompt injection protection
- [ ] Add user feedback

## Progress Log

Use this section weekly.

### Week 1

- Learned:
- Built:
- Failed:
- Fixed:
- Next:

### Week 2

- Learned:
- Built:
- Failed:
- Fixed:
- Next:

### Week 3

- Learned:
- Built:
- Failed:
- Fixed:
- Next:

### Week 4

- Learned:
- Built:
- Failed:
- Fixed:
- Next:

## Personalization Questions

Answer these later to tailor the plan further:

1. What is your current tech stack?
2. How many years of software engineering experience do you have?
3. What type of company/domain do you work in?
4. Is your main goal job safety, salary growth, freelancing, or indie product income?
5. How many hours per week can you realistically spend?
6. Do you prefer backend, frontend, full-stack, devtools, data, or product engineering?

## Final Direction

Your safest path is:

**Stay strong at software engineering, then layer practical AI product engineering on top.**

Do not become only a prompt user. Become the engineer who can design, build, evaluate, debug, and ship AI-powered systems.
