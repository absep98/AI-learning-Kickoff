# Day 08 — Terminal Chatbot (Ollama + phi3:mini)

> Previous: [Day 07 — Pipeline Made Real](day-07-pipeline-hands-on.md)

## What This Day Is About

Built a working terminal chatbot from scratch in Python. This is the first real AI application — not a demo, not a playground experiment, but actual code that manages conversation history, streams responses token-by-token, and uses a system prompt to shape behavior.

Every concept from Days 1–7 shows up in this code.

---

## 1. What Was Built

A Python script (`projects/day-08-chatbot/chat.py`) that:
- Runs in the terminal
- Takes user input in a loop
- Maintains full conversation history (solving statelessness)
- Sends history to Ollama's local API every turn
- Streams the response token-by-token (ChatGPT-style typing effect)
- Uses a system prompt to define the AI's personality

### The interaction
```
You: What is a goroutine?
AI: A goroutine is a lightweight thread managed by the Go runtime...

You: give me a simple code example
AI: Certainly! Let's consider... [gives goroutine example without being told the topic]

You: quit
```

The second message proved context memory — the model knew to give a goroutine example because the full conversation history was re-sent.

---

## 2. The 4-Step Loop — Core of Every Chat Application

Every time the user sends a message, the script does exactly 4 things:

```
1. Take user input
2. Append user message to conversation history
3. Send full history to Ollama API
4. Append AI response to conversation history
```

This loop repeats forever until the user types "quit". The history list grows each turn — that's how you fake memory on a stateless model.

**This is the same pattern used by ChatGPT, Claude, and every chat product.** The only differences are the model, the API endpoint, and the UI.

---

## 3. The Code — Line by Line Breakdown

```python
import requests
import json
```
Standard libraries. `requests` for HTTP calls to Ollama. `json` to parse streaming response lines.

```python
conversation_history = [
    {"role": "system", "content": "You are a distinguished Go engineer..."}
]
```
The history starts with the system prompt. This is the first message the model sees every request. It shapes behavior without the user seeing it. The list format with `role` and `content` is the **universal chat message format** — same structure used by OpenAI, Anthropic, Google, and Ollama.

```python
while True:
    prompt_input = input("\nYou: ")
    if prompt_input == "quit":
        break
```
Infinite loop with exit condition. Simple REPL (Read-Eval-Print Loop) pattern.

```python
    conversation_history.append({"role": "user", "content": prompt_input})
```
**Step 2 — append before sending.** The user's message is added to history so it gets included in the API call. Without this, the model would never see what the user just typed.

```python
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={"model": "phi3:mini", "messages": conversation_history, "stream": True},
        stream=True
    )
```
**Step 3 — send full history.** Key observations:
- `http://localhost:11434` — Ollama runs locally on this port
- `/api/chat` — the chat endpoint (not `/api/generate` which is for single prompts)
- `messages: conversation_history` — the ENTIRE conversation goes every time. Turn 10 sends all 10 previous messages plus the system prompt
- `stream: True` in both the JSON body AND the requests parameter — body tells Ollama to stream, parameter tells requests to not buffer the response

```python
    full_response = ""
    for line in response.iter_lines():
        if line:
            chunk = json.loads(line.decode('utf-8'))
            token = chunk.get("message", {}).get("content", "")
            print(token, end="", flush=True)
            full_response += token
```
**Streaming loop.** Ollama sends one JSON object per token. Each looks like:
```json
{"message": {"content": "A"}, "done": false}
```
The code parses each line, extracts the token, prints it immediately (`flush=True` forces the terminal to display it right away), and accumulates the full response.

```python
    conversation_history.append({"role": "assistant", "content": full_response})
```
**Step 4 — append after receiving.** The model's response is added to history so the NEXT request includes it. Without this line, the model would forget its own previous answers.

---

## 4. What Each Concept From Days 1–7 Looks Like in This Code

| Concept | Where it appears |
|---|---|
| **Statelessness (Day 05)** | `messages: conversation_history` — re-sending everything every turn because the model remembers nothing |
| **System prompt (Day 05)** | First item in the history list with `role: "system"` |
| **Streaming (Day 05)** | `stream: True` + `iter_lines()` loop — token-by-token delivery |
| **Chat message format (Day 05)** | `{"role": "user/assistant/system", "content": "..."}` — universal format |
| **HTTP API pattern (Day 06)** | `requests.post("http://localhost:11434/api/chat")` — the chat UI is just an HTTP wrapper |
| **Token-by-token generation (Day 06)** | Each `chunk` in the streaming loop is one token — you can see the model "thinking" |
| **Memory is fake (Day 06)** | History list in Python, not in the model. Your code IS the memory system |
| **Context window (Day 02)** | History grows every turn. Eventually it will exceed phi3:mini's context limit and break |

---

## 5. What This Proves

### Statelessness is real and visible
Without `conversation_history.append(...)` for both user and assistant messages, the model would treat every message as a brand new conversation. The second question "give me a simple code example" would have no idea you were talking about goroutines.

### The "memory" is your code, not the model
The entire memory system is one Python list. That's it. ChatGPT's "memory" is the same thing — a list of messages managed by the application, not by the model.

### Chat UI = HTTP POST
The fancy chat interfaces are just wrappers around `requests.post()`. What we built in the terminal is architecturally identical to what ChatGPT does — different UI, same engineering.

### System prompts shape everything
The model responded as a Go engineer because the system prompt told it to. Same model, different system prompt → completely different personality. This is how AI products differentiate.

### Small models are verbose and imprecise
phi3:mini generated long, over-explained responses with questionable code quality. A larger model (GPT-4, Claude) with this exact same code would give much better answers. The engineering doesn't change — only the model name in the API call.

---

## 6. What's Not Handled Yet (Future Improvements)

| Missing feature | Why it matters |
|---|---|
| **Context window overflow** | History grows forever. After enough turns, it will exceed phi3:mini's limit and crash or produce garbage |
| **Error handling** | If Ollama isn't running, the script crashes with a connection error |
| **Token counting** | No way to know how close you are to the context limit |
| **Temperature control** | Hardcoded — no way to adjust creativity on the fly |
| **Conversation saving** | History disappears when you quit. No persistence |

These are not bugs — they are the natural next steps in building a production-grade chat system.

---

## Key Takeaways

**The 4-step loop is everything.** Input → append → send full history → append response. This is the core of every chat application.

**Statelessness is solved by the application, not the model.** One Python list is the entire memory system.

**Streaming is just a loop over JSON lines.** Each line is one token. Print immediately for the typing effect.

**The universal message format** (`role` + `content`) works across Ollama, OpenAI, Anthropic, and Google. Learn it once, use it everywhere.

**Chat UI = HTTP API wrapper.** Everything you see in ChatGPT is just a prettier version of what we built in 30 lines.

---

## One-Line Summaries

**4-step chat loop:** Take input → append to history → send full history to API → append response to history. Repeat forever.

**Statelessness solved:** The conversation history list in your code IS the memory. The model has none.

**Streaming:** Ollama sends one JSON line per token. Parse, print with flush, accumulate. That's the ChatGPT typing effect.

**System prompt:** First message in history with role "system". Defines personality. User never sees it but it shapes every response.

**Universal message format:** `{"role": "user|assistant|system", "content": "..."}` — same across all major LLM APIs.

---

## Revision Questions

1. **What are the 4 steps your chatbot does every time the user sends a message?**
2. **Why do you send the FULL conversation history every request, not just the latest message?**
3. **What would happen if you removed the line that appends the assistant's response to history?**
4. **What would happen if you removed the line that appends the user's message to history?**
5. **The system prompt is the first item in the history list. Does the user see it? What does it do?**
6. **Explain what `stream=True` does in both the JSON body and the `requests.post()` parameter.**
7. **Your chatbot works with phi3:mini locally. What would you change to make it work with OpenAI's GPT-4 instead?** *(Hint: very little)*
8. **After 100 turns of conversation, what problem will your chatbot hit? How would you solve it?**
9. **Someone says "ChatGPT remembers everything I've ever said." Is that the model remembering, or something else?**
10. **You built this in ~30 lines of Python. What does that tell you about where the "intelligence" actually lives?**
