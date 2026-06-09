import os
import json
import requests
import math

OLLAMA_URL_EMBEDDING = "http://localhost:11434/api/embed"
MODEL = "all-minilm"


def load_chunks(folder_path):
    chunks = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".md"):
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as file:
                content = file.read()
            paragraphs = content.split("\n\n")
            chunks.extend([p.strip() for p in paragraphs if p.strip() and len(p.strip()) > 80])

    return chunks

documents = load_chunks(r"C:\learning\aithings\days")


embeddings = {}

for i, document in enumerate(documents):
    resp = requests.post(OLLAMA_URL_EMBEDDING, json={"model": MODEL, "input": document})
    vector = resp.json()["embeddings"][0]
    embeddings[document] = vector
    if i % 50 == 0:
        print(f"Embedding chunk {i}/{len(documents)}...")


def cosine_similarity(vec_a, vec_b):
    dot = sum(a*b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a*a for a in vec_a))
    mag_b = math.sqrt(sum(b*b for b in vec_b))
    return dot/(mag_a * mag_b)


while True:

    result = []

    query = input("\nYou: ").strip()
    if not query or query == "quit":
        break

    query_resp = requests.post(OLLAMA_URL_EMBEDDING, json={"model": MODEL, "input": query})
    query_vector = query_resp.json()["embeddings"][0]

    for doc, doc_vector in embeddings.items():
        score = cosine_similarity(query_vector, doc_vector)
        result.append((doc, score))

    result.sort(key=lambda x: x[1], reverse=True)
    context = "\n\n".join([doc for doc, score in result[:3]])

    user_message = f"Use only the context below to answer.\n\nContext:\n{context}\n\nQuestion: {query}"

    conversation_history = [
        {"role": "system", "content": "You are a helpful assistant. Answer only from the provided context."},
        {"role": "user", "content": user_message}
    ]

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={"model": "phi3:mini", "messages": conversation_history, "stream": True},
        stream=True
    )

    print("\nAI: ", end="", flush=True)
    full_response = ""
    for line in response.iter_lines():
        if line:
            chunk = json.loads(line.decode('utf-8'))
            token = chunk.get("message", {}).get("content", "")
            print(token, end="", flush=True)
            full_response += token

    print()
