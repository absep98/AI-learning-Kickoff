import requests
import math

documents = [
    "Goroutines are lightweight threads managed by the Go runtime.",
    "Channels are how goroutines communicate safely.",
    "Go's garbage collector is concurrent and low-latency.",
    "Redis is an in-memory key-value store often used as a cache.",
    "PostgreSQL is a relational database with strong ACID guarantees.",
    "Kubernetes orchestrates containerized applications across clusters.",
    "A transformer uses attention to weigh relationships between tokens.",
    "Embeddings convert text into vectors that encode meaning.",
    "Cosine similarity measures the angle between two vectors.",
    "Temperature controls how the model samples its next token.",
]


OLLAMA_URL = "http://localhost:11434/api/embed"
MODEL = "all-minilm"  # dedicated embedding model 


# Get Embeddings for all texts
embeddings = {}

for document in documents:
    resp = requests.post(OLLAMA_URL, json={"model" : MODEL, "input" : document})
    # Internally: tokenize → embed each token → self-attention → POOL all token vectors into one sentence vector
    vector = resp.json()["embeddings"][0]
    embeddings[document] = vector
    # show first 5 dimensions
    print(f'"{document}"')
    print(f"  Vector length: {len(vector)} dimensions")
    print(f"  First 5 values: [{', '.join(f'{v:.4f}' for v in vector[:5])}...]")
    print()

#  Cosing similarity: prove similar meanings = close vectors

def cosine_similarity(vec_a, vec_b):
    dot = sum(a*b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a*a for a in vec_a))
    mag_b = math.sqrt(sum(b*b for b in vec_b))

    return dot/(mag_a * mag_b)


print("=" * 60)
print("COSINE SIMILARITY - Does meaning = closeness")
print("=" * 60)


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
    print("\nTop 3 results:")
    for doc, score in results[:3]:
        print(f"  {score:.4f}  {doc}")

