import os
import chromadb
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

load_dotenv(r"C:\learning\aithings\.env")

DISTANCE_THRESHOLD = 0.75

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path=os.getenv("CHROMA_DB_PATH", r"C:\learning\aithings\projects\day-14-chromadb\chroma_db"))
collection = client.get_collection(name="ai_notes")
ALLOWED_ACTIONS = {"read_progress_files", "summarize_status", "ask_clarification", "check_git_status", "answer_question"}
REPO_ROOT = Path(os.getenv("REPO_ROOT", r"C:\learning\aithings"))


def retrieve_chunks(query, n_results=5):
    """
    Embeds the query using the local sentence-transformers model (no network
    call, no Ollama dependency — runs anywhere the Python process runs),
    then queries ChromaDB for the closest matching note chunks.

    Returns (texts, metas, distances) — the retrieved chunk text, their
    source metadata, and cosine distance (lower = more similar) for each.
    Does NOT call the LLM here — that happens in answer_question().
    """
    query_vector = embed_model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    texts = results["documents"][0]
    metas =  results["metadatas"][0]
    distances = results["distances"][0]

    return (texts, metas, distances)

def plan_action(query):
    query = query.lower()

    if "git" in query or "status" in query or "commit" in query or "branch" in query:
        return "check_git_status"

    if "day" in query or "progress" in query or "roadmap" in query:
        return "read_progress_files"

    return "answer_question"

def answer_question(query):
    texts, metas, distances = retrieve_chunks(query)

    if not texts or distances[0] > DISTANCE_THRESHOLD:
        return {"ok": "true", "message": "No relevant notes found for that question."}

    context = "\n\n".join(texts)
    sources = sorted(set(m["source"] for m in metas))

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        temperature=0,
        messages=[
            {"role": "system", "content": "Answer only using the provided context. Be concise."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
        ],
    )
    answer = response.choices[0].message.content.strip()
    return {"ok": "true", "message": f"{answer} (sources: {', '.join(sources)})"}

def check_git_status():
    import subprocess
    try:
        result = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "status", "--short"],
            capture_output=True,
            text=True,
            check=False
        )
        lines = result.stdout.strip()
        summary = f"{len(lines.splitlines())} changed file(s)" if lines else "working tree clean"
        return {"ok": "true", "message": f"Git status: {summary}"}
    except OSError as err:
        return {"ok": "false", "message": f"git error: {err}"}


def read_progress_files():
    progress_path = REPO_ROOT / "progress.md"
    try:
        lines = progress_path.read_text(encoding="utf-8").splitlines()
        focus_line = next((ln for ln in lines if ln.startswith("**Current Day:**")), "**Current Day:** unknown")
        goal_line = next((ln for ln in lines if ln.startswith("**Main Goal:**")), "**Main Goal:** unknown")
        return {"ok": "true", "message": f"{focus_line} | {goal_line}"}
    except OSError as err:
        return {"ok": "false", "message": f"file read error: {err}"}


def model_plan_action(intent, context="", history=None):
    if not groq_client:
        return plan_action(intent)

    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an action planner. Return ONLY one action string from this set: "
                    "answer_question, check_git_status, read_progress_files. "
                    "Use check_git_status for anything about git, commits, branches, or repo status. "
                    "Use read_progress_files for questions about current day, progress, or what's next in the learning plan. "
                    "Use answer_question for anything else, including questions about notes or concepts. "
                    "No JSON, no explanation."
                ),
            },
        ]

        # Add previous steps as conversation history so model has memory
        for h in (history or []):
            messages.append({"role": "user", "content": h["intent"]})
            messages.append({"role": "assistant", "content": h["action"]})

        messages.append({"role": "user", "content": f"Intent: {intent}\nContext: {context}\n"})

        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0,
            messages=messages
        )

        action = response.choices[0].message.content.strip().lower()
        action = action.replace("`", "").replace('"', "").replace("'", "")
        action = action.splitlines()[0].strip()

        if action in ALLOWED_ACTIONS:
            return action

        return plan_action(intent)
    except Exception:
        return plan_action(intent)


if __name__ == "__main__":
    print(check_git_status()["message"])
    print(read_progress_files()["message"])
    print(retrieve_chunks("what is temperature")[2][0])  # prints the top distance