import chromadb
import os
import json
import requests
from groq import Groq
from dotenv import load_dotenv
load_dotenv(r"C:\learning\aithings\.env")

groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])

OLLAMA_URL_EMBEDDING = "http://localhost:11434/api/embed"
MODEL = "all-minilm"

SKIP_FILES = {"day-12-rag-improved.md"}  # day-11 re-included so chunking/RAG questions work

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
client = chromadb.PersistentClient(path=r"C:\learning\aithings\projects\day-14-chromadb\chroma_db")

# get or create a collection like a table in db

collection = client.get_or_create_collection(
    name="ai_notes",
    metadata={"hnsw:space": "cosine"}  # use cosine distance, not L2
)

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


def query_rag(query):
    """
    Query the RAG system and return structured response
    Returns: dict with keys 'answer', 'confidence', 'sources'
    """
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

    # Cosine distance: lower = more similar. Refuse if best match > 0.75
    if distances[0] > 0.75:
        return {
            "answer": "I don't have relevant information about that in my notes.",
            "confidence": "none",
            "sources": []
        }

    sources = list(set([m["source"] for m in metas]))
    context = "\n\n".join(texts)

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Answer only from the provided context. Respond with ONLY a valid JSON object: {\"answer\": \"...\", \"confidence\": \"high|medium|low\"}"},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
        ]
    )
    full_response = response.choices[0].message.content.strip()

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
        return {
            "answer": parsed.get("answer", ""),
            "confidence": parsed.get("confidence", "unknown"),
            "sources": sources
        }
    except (json.JSONDecodeError, KeyError):
        return {
            "answer": full_response,
            "confidence": "error",
            "sources": sources
        }


def interactive_loop():
    """Run interactive query loop"""
    while True:
        query = input("\nYou: ").strip()
        if not query or query == "quit":
            break

        result = query_rag(query)
        
        print("\nAI:")
        print(f"Answer: {result['answer']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Sources: {', '.join(result['sources'])}")
        print()


if __name__ == "__main__":
    interactive_loop()
