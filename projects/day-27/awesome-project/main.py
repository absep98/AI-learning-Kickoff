from fastapi import FastAPI
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