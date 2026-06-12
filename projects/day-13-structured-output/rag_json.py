import os
import json
import requests
import math

OLLAMA_URL_EMBEDDING = "http://localhost:11434/api/embed"
MODEL = "all-minilm"
CACHE_FILE = r"C:\learning\aithings\projects\day-12-rag-improved\embeddings.json"

SKIP_FILES = {"day-11-rag-over-notes.md", "day-12-rag-improved.md"}

def load_chunks(folder_path):
    chunks = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".md") and filename not in SKIP_FILES:
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as file:
                content = file.read()
            paragraphs = content.split("\n\n")
            chunks.extend([(p.strip(), filename) for p in paragraphs if p.strip() and len(p.strip()) > 80])

    return chunks

documents = load_chunks(r"C:\learning\aithings\days")


embeddings = {}

if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        embeddings = json.load(f)
    print(f"Loaded {len(embeddings)} embeddings from cache.")

else:
    for i, (text, source) in enumerate(documents):
        resp = requests.post(OLLAMA_URL_EMBEDDING, json={"model": MODEL, "input": text})
        vector = resp.json()["embeddings"][0]
        embeddings[text] = {"source": source, "vector": vector}

        if i % 50 == 0:
            print(f"Embedding chunk {i}/{len(documents)}...")
    
    with open(CACHE_FILE, "w") as f:
        json.dump(embeddings, f)
    print("Embeddings saved to cache.")


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

    for text, data in embeddings.items():
        score = cosine_similarity(query_vector, data["vector"])
        result.append((text, data["source"], score))

    result.sort(key=lambda x: x[2], reverse=True)

    # Deduplicate: max 1 chunk per source file, take top 5 across different sources
    seen_sources = {}
    deduped = []
    for text, source, score in result:
        if source not in seen_sources:
            seen_sources[source] = 0
        if seen_sources[source] < 2:  # max 2 chunks per file
            deduped.append((text, source, score))
            seen_sources[source] += 1
        if len(deduped) == 5:
            break
    result = deduped

    if result[0][2] < 0.4:
        print("\nAI: I don't have relevant information about that in my notes.")
        continue
    context = "\n\n".join([text for text, source, score in result[:5]])

    print("\nRetrieved chunks:")
    for text, source, score in result[:5]:
        print(f"  [{score:.3f}] ({source}) {text[:80]}...")
    sources = list(set([source for text, source, score in result[:5]]))
    print(f"Sources: {', '.join(sources)}")
    
    user_message = f"Use only the context below to answer.\n\nContext:\n{context}\n\nQuestion: {query}"

    conversation_history = [
        {"role": "system", "content": "You are a helpful assistant. Answer only from the provided context. You MUST respond with ONLY a valid JSON object in this exact format, no other text: {\"answer\": \"your answer here\", \"confidence\": \"high or medium or low\"}"},
        {"role": "user", "content": user_message}
    ]

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={"model": "phi3:mini", "messages": conversation_history, "stream": False},
        stream=False
    )

    print("\nAI: ", end="", flush=True)
    full_response = response.json()["message"]["content"].strip()
    # Strip markdown code fences if model wraps JSON in ```json ... ```
    if full_response.startswith("```"):
        full_response = full_response.split("```")[-2] if "```" in full_response else full_response
        full_response = full_response.lstrip("json").strip()
    # Extract just the JSON object if model added extra text after it
    start = full_response.find("{")
    end = full_response.rfind("}") + 1
    if start != -1 and end > start:
        full_response = full_response[start:end]
    try:
        parsed = json.loads(full_response)
        print(f"\nAnswer: {parsed['answer']}")
        print(f"Confidence: {parsed['confidence']}")
        print(f"Sources: {', '.join(sources)}")
    except (json.JSONDecodeError, KeyError):
        print(f"\n[Model did not return valid JSON. Raw response:]")
        print(full_response)
    print()
