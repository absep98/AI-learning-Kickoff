import requests
import math
import json

documents = [
    "Goroutines are lightweight threads managed by the Go runtime.",
    "Channels are how goroutines communicate safely.",
    "Go's garbage collector is concurrent and low-latency.",
    "Redis is an in-memory key-value store often used as a cache",
    "PostgreSQL is a relational database with strong ACID guarantees.",
    "Kubernetes orchestrates containerized applications across clusters.",
    "A transformer uses attention to weigh relationships between tokens.",
    "Embeddings convert text into vectors that encode meaning.",
    "Cosine similarity measures the angle between two vectors.",
    "Temperature controls how the model samples its next token.",
]


OLLAMA_URL = "http://localhost:11434/api/embed"
MODEL = "all-minilm"

embeddings = {}

for document in documents:
    resp = requests.post(OLLAMA_URL, json={"model" : MODEL, "input" : document})
    # it tokenize and then embed each token does the self attention and pool all token vector
    # into one sentence vector
    vector = resp.json()["embeddings"][0]
    embeddings[document] = vector


def cosine_similarity(vec_a, vec_b):
    dot = sum(a*b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a*a for a in vec_a))
    mag_b = math.sqrt(sum(b*b for b in vec_b))

    return dot/(mag_a * mag_b)


while True:
    results = []
    query = input()
    if query == 'quit':
        break

    query_resp = requests.post(OLLAMA_URL, json={"model" : MODEL, "input" : query})
    query_vector = query_resp.json()["embeddings"][0]

    for doc, doc_vector in embeddings.items():
        score = cosine_similarity(query_vector, doc_vector)
        results.append((doc, score))

    results.sort(key=lambda x: x[1], reverse=True)
    context = "\n".join([doc for doc,score in results[:3]])

    user_message = f"Use only the context below to answer.\n\nContext:\n{context}\n\nQuestion: {query}"

    conversation_history = [
        {"role": "system", "content": "You are a helpful assistant. Answer only from the provided context."},
        {"role": "user", "content": user_message}
    ]

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={"model": "phi3:mini", "messages": conversation_history, "stream" : True},
        stream=True
    )

    full_response = ""
    for line in response.iter_lines():
        if line:
            chunk = json.loads(line.decode('utf-8'))
            token = chunk.get("message", {}).get("content", "")
            print(token, end="", flush=True)
            full_response += token

    print()
