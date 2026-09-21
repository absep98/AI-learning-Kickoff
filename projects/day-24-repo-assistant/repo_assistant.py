import os
import requests
import chromadb
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv(r"C:\learning\aithings\.env")

OLLAMA_URL_EMBEDDING = "http://localhost:11434/api/embed"
EMBED_MODEL = "all-minilm"
DISTANCE_THRESHOLD = 0.75

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

client = chromadb.PersistentClient(path=r"C:\learning\aithings\projects\day-14-chromadb\chroma_db")
collection = client.get_collection(name="ai_notes")
ALLOWED_ACTIONS = {"read_progress_files", "summarize_status", "ask_clarification", "check_git_status", "answer_question"}
REPO_ROOT = Path(r"C:\learning\aithings")

def retrieve_chunks(query, n_results=5):
    """
    TODO (you write this):
    1. Call OLLAMA_URL_EMBEDDING with requests.post, same shape as rag_chroma.py:
       json={"model": EMBED_MODEL, "input": query}
       Get the vector out of resp.json()["embeddings"][0]
    2. Call collection.query(query_embeddings=[vector], n_results=n_results,
       include=["documents", "metadatas", "distances"])
    3. Pull out texts = results["documents"][0], metas = results["metadatas"][0],
       distances = results["distances"][0]
    4. Return (texts, metas, distances) as a tuple.

    Do NOT call the LLM in here — this function only does retrieval.
    """
    query_resp = requests.post(OLLAMA_URL_EMBEDDING, json={"model": EMBED_MODEL, "input": query})
    query_vector = query_resp.json()["embeddings"][0]

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


def plan_action(query):
    query = query.lower()

    if "git" in query or "status" in query or "commit" in query or "branch" in query:
        return "check_git_status"

    return "answer_question"


if __name__ == "__main__":
    while True:
        query = input("Ask about your notes: ").strip()

        if not query or query.lower() in ["quit", "exit"]:
            break

        action = plan_action(query)
        if action == "answer_question":
            result = answer_question(query)
        elif action == "check_git_status":
            result = check_git_status()

        print(result["message"])