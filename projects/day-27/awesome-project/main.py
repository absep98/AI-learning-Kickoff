from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from assistant import retrieve_chunks, model_plan_action, answer_question, check_git_status, read_progress_files


# Pydantic BaseModel: describes the SHAPE of expected JSON, not behavior.
# FastAPI auto-validates incoming request bodies against this before your
# function runs, and converts valid JSON into a real Question object
# (so question.text works like any object attribute, e.g. log.action).
# Invalid input (missing/wrong-type field) -> FastAPI returns 422 automatically,
# your function code never even executes.
class Question(BaseModel):
    text: str

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World!"}

@app.get("/greet")
async def greet(name: str):
    return {"message": f"Hello {name}!"}


# Path parameter: {name} is part of the URL structure itself.
# Visit: http://127.0.0.1:8000/greet-path/aks
# Good for identifying a specific resource (e.g. a user ID), required, no ?key=value.
@app.get("/greet-path/{name}")
async def greet_path(name: str):
    return {"message": f"Hello {name}! (via path)"}


# Query parameter: name is a plain function argument, NOT in the path string.
# Visit: http://127.0.0.1:8000/greet-query?name=aks
# Good for optional/filter-like values, appended after "?" in the URL.
@app.get("/greet-query")
async def greet_query(name: str):
    return {"message": f"Hello {name}! (via query)"}

@app.post("/ask")
async def ask(question: Question):
    # question is a Question object here, not a raw dict — FastAPI already
    # validated + parsed the JSON body against the BaseModel above.
    action = model_plan_action(question.text)
    if action == "check_git_status":
        result = check_git_status()
    elif action == "read_progress_files":
        result = read_progress_files()
    else:
        result = answer_question(question.text)
    return result


# Simple frontend so this feels like a real product, not just a raw JSON API.
# Kept on a separate path from "/" so Render's health check ("/") stays fast.
CHAT_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Repo Assistant</title>
<style>
  body { font-family: system-ui, sans-serif; max-width: 640px; margin: 40px auto; padding: 0 16px; }
  h1 { font-size: 1.4rem; }
  #question { width: 100%; padding: 10px; font-size: 1rem; box-sizing: border-box; }
  #ask-btn { margin-top: 8px; padding: 8px 16px; font-size: 1rem; cursor: pointer; }
  #answer { margin-top: 20px; white-space: pre-wrap; line-height: 1.5; }
  .hint { color: #666; font-size: 0.9rem; }
</style>
</head>
<body>
  <h1>Ask Repo Assistant</h1>
  <p class="hint">Ask about the learning notes (e.g. "what is temperature"), or try "check git status" / "what day am I on".</p>
  <p class="hint">Note: this runs on a free-tier server that sleeps after inactivity — the first question after a while may take up to a minute to respond.</p>
  <input id="question" type="text" placeholder="Ask a question..." />
  <button id="ask-btn">Ask</button>
  <div id="answer"></div>

<script>
  const input = document.getElementById("question");
  const button = document.getElementById("ask-btn");
  const answerBox = document.getElementById("answer");

  async function askQuestion() {
    const text = input.value.trim();
    if (!text) return;

    answerBox.textContent = "Thinking... (may take up to a minute if the server was asleep)";
    button.disabled = true;

    try {
      const response = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      const data = await response.json();
      answerBox.textContent = data.message || "No response.";
    } catch (err) {
      answerBox.textContent = "Error: " + err.message;
    } finally {
      button.disabled = false;
    }
  }

  button.addEventListener("click", askQuestion);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") askQuestion();
  });
</script>
</body>
</html>
"""


@app.get("/chat", response_class=HTMLResponse)
async def chat_page():
    return CHAT_PAGE