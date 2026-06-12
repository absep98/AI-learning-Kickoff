import chromadb
import os
import json
import requests

OLLAMA_URL_EMBEDDING = "http://localhost:11434/api/embed"
MODEL = "all-minilm"

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


# create persistent client - stores data in ./chroma_db folder
client = chromadb.PersistentClient(path="./chroma_db")

# get or create a collection like a table in db

collection = client.get_or_create_collection(name="ai_notes")

if collection.count() == 0:
    print("Populating chromaDB...")
    texts = []
    vectors = []
    metadatas = []
    ids = []

    for i, (text, source) in enumerate(documents):
        resp = requests.post(OLLAMA_URL_EMBEDDING, json={"model": MODEL, "input": text})
        vector = resp.json()["embeddings"][0]
        texts.append(text)
        vectors.append(vector)
        metadatas.append({"source": source})
        ids.append(str(i))

        if i%50 == 0:
            print(f"Embedding chunk {i}/{len(documents)}...")

    # embed and add document
    collection.add(
        documents=texts,
        embeddings=vectors,
        metadatas=metadatas,
        ids=ids
    )

    print(f"Added {collection.count()} chunks to chromaDB.")
else:
    print(f"Loaded {collection.count()} chunks from chromaDB.")


while True:

    query = input("\nYou: ").strip()
    if not query or query == "quit":
        break

    query_resp = requests.post(OLLAMA_URL_EMBEDDING, json={"model": MODEL, "input": query})
    query_vector = query_resp.json()["embeddings"][0]

    # ChromaDB does the similarity search — no manual cosine loop needed
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=5,
        include=["documents", "metadatas", "distances"]
    )

    texts = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    # Distance < 0.6 means relevant (lower distance = more similar in ChromaDB)
    if distances[0] > 0.6:
        print("\nAI: I don't have relevant information about that in my notes.")
        continue

    print("\nRetrieved chunks:")
    for text, meta, dist in zip(texts, metas, distances):
        print(f"  [dist={dist:.3f}] ({meta['source']}) {text[:80]}...")

    sources = list(set([m["source"] for m in metas]))
    print(f"Sources: {', '.join(sources)}")

    context = "\n\n".join(texts)
    
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
