Deep Dive into LLMs (Andrej Karpathy)
	https://youtu.be/7xTGNNLPyMI

How I use LLMs (Andrej Karpathy)
	https://youtu.be/EWvNQjAaOHw

DeepLearning.AI Short Courses
	All Short Courses (Filter: AI Coding)

Open Source AI Courses for Beginners (Microsoft)
	https://microsoft.github.io/generative-ai-for-beginners/
https://microsoft.github.io/ai-agents-for-beginners/
https://github.com/microsoft/mcp-for-beginners

Context Engineering
	Guidelines, see also "Context Engineering" at AI Engineering: Getting Started
* Stating the obvious: When you are going to change the topic or start working on a new task, always create a new chat thread.
* Minimize the set of tools you have enabled. Tool descriptions take valuable context space. Use tool sets, or custom agents with specific sets of tools.
* Monitor the context consumed by your session. The closer you approach the max context limit of the model, the worse it will perform (aka "context rot"). Modern agents perform compaction automatically. But don't hesitate to initiate it manually when context grows, especially at points in the conversation where detailed previous context is no longer needed.
* When your last request(s) to the agent didn't have the intended outcome, don't try to put it on the right track by continuing the conversation. Instead, use the "restore checkpoint", "rewind code", "fork conversation", etc. feature to go back to a point in the chat, where you can rephrase your request(s).
* Use progressive disclosure. Initially you may start with one big instructions / rules / AGENTS.md / CLAUDE.md file. But as it grows, start treating it as a repository navigation map or table of contents. Put only crucial information and provide enough guidance, so that the agent can understand how to explore your repository and where to find more details. Leverage the directory scoping / nesting supported by these files.
* For specific workflows, use agent skills. Progressive disclosure is a feature.
* For more advanced workflows, use custom agents, as a way of implementing context isolation. Running them as subagents separates their context from the main thread. Handoffs between custom agents become the boundary when context compaction takes place. If you want to be in full control, use markdown files for carrying context forward (aka context offloading).
* For larger or complex features/tasks, divide your chat sessions in research, plan, implement (or other) steps. Also, split your implementation in multiple phases and be deliberate in terms of what context you carry between each step or phase. Again, use markdown files for carrying that context forward.


AI Coding Benchmarks/Leaderboards
	https://arena.ai/leaderboard/code
https://artificialanalysis.ai/agents/coding-agents
https://epoch.ai/benchmarks
https://www.swebench.com/verified.html
https://www.tbench.ai/leaderboard
https://scale.com/leaderboard/swe_bench_pro_public
https://scale.com/leaderboard/sweatlas-qna :new:
https://labs.scale.com/leaderboard/sweatlas-tw :new:
https://labs.scale.com/leaderboard/sweatlas-refactoring :new:
https://cursor.com/blog/cursorbench :new:
https://deepswe.datacurve.ai/ :new:
https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/

GitHub Copilot AI Model Comparison
	https://docs.github.com/en/copilot/reference/ai-models/model-comparison

GPT-4.1/5/5.x Prompting Guides (OpenAI)
	GPT-4.1 Prompting Guide
GPT-5 Prompting Guide
GPT-5.1 Prompting Guide
GPT-5.2 Prompting Guide
GPT-5.3 Codex Prompting Guide
Prompt Guidance for GPT-5.4 :new:
Prompt Guidance for GPT-5.5 :new:

Claude Prompting Guides (Anthropic)
	(Claude) Models Overview
(Claude) Prompting Best Practices
What's new in Claude Opus 4.8 :new:

Community collections of instructions, rules, prompts, custom agents, plugins, etc.
	GitHub Copilot: https://github.com/github/awesome-copilot
Windsurf Rules: https://windsurf.run/rules

Agent skills collections
	Anthropic: https://github.com/anthropics/skills
Microsoft: https://microsoft.github.io/skills/
Vercel: https://skills.sh/

Agent plugins collections
	Anthropic: https://github.com/anthropics/claude-code/tree/main/plugins
Microsoft: https://github.com/github/awesome-copilot/tree/main/plugins
Microsoft: https://github.com/github/copilot-plugins

Claude Code
	Best practices for Claude Code
The Complete Guide to Building Skills for Claude
Lessons from building Claude Code: How we use skills
How and when to use subagents in Claude Code
Using Claude Code: Session management and 1M context :new:
Best practices for using Claude Opus 4.7 with Claude Code :new:
How Claude Code works in large codebases: Best practices and where to start :new:
Using Claude Code: The unreasonable effectiveness of HTML :new:
A harness for every task: Dynamic workflows in Claude Code :new:

