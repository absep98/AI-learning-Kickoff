import chromadb
import os
import json
import re
import requests
from groq import Groq
from dotenv import load_dotenv
load_dotenv(r"C:\learning\aithings\.env")

groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])

OLLAMA_URL_EMBEDDING = "http://localhost:11434/api/embed"
MODEL = "all-minilm"

SKIP_FILES = {"day-12-rag-improved.md"}  # day-11 re-included so chunking/RAG questions work


def _tokenize(text):
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    preview = text.replace("\n", " ")[:80]
    print(f"[TOKENIZE] text='{preview}' -> tokens(first 12)={tokens[:12]}")
    return tokens


def _rerank_results(query, texts, metas, distances, top_k=5):
    """
    Hybrid rerank: semantic score from Chroma distance + lexical overlap with query terms.
    This helps pull exact-fact chunks (model names, numbers) higher in the final context.
    """
    query_terms = {t for t in _tokenize(query) if len(t) > 2}
    print(f"[RERANK] query_terms={sorted(query_terms)}")
    scored = []

    for idx, (text, meta, dist) in enumerate(zip(texts, metas, distances)):
        doc_terms = set(_tokenize(text))
        overlap = 0.0
        if query_terms:
            overlap = len(query_terms & doc_terms) / len(query_terms)

        semantic = 1.0 - float(dist)  # cosine distance -> similarity proxy
        combined = semantic + (0.30 * overlap)
        source = meta.get("source", "unknown") if isinstance(meta, dict) else "unknown"
        print(
            "[RERANK] "
            f"cand={idx} source={source} dist={float(dist):.4f} "
            f"semantic={semantic:.4f} overlap={overlap:.4f} combined={combined:.4f}"
        )
        scored.append((combined, text, meta, dist))

    scored.sort(key=lambda x: x[0], reverse=True)
    selected = scored[:top_k]

    print("[RERANK] top candidates after sorting:")
    for rank, item in enumerate(selected, start=1):
        _, _, meta, dist = item
        source = meta.get("source", "unknown") if isinstance(meta, dict) else "unknown"
        print(f"[RERANK] rank={rank} source={source} dist={float(dist):.4f}")

    out_texts = [x[1] for x in selected]
    out_metas = [x[2] for x in selected]
    out_distances = [x[3] for x in selected]
    return out_texts, out_metas, out_distances

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
    retrieval_query = query
    q_lower = query.lower()
    if "embedding" in q_lower and "model" in q_lower:
        retrieval_query += " all-minilm"
    if "groq" in q_lower and ("model" in q_lower or "llm" in q_lower):
        retrieval_query += " llama-3.1-8b-instant llama 3.1 8b"
    print(f"[QUERY] user_query='{query}'")
    print(f"[QUERY] retrieval_query='{retrieval_query}'")

    query_resp = requests.post(OLLAMA_URL_EMBEDDING, json={"model": MODEL, "input": retrieval_query})
    query_vector = query_resp.json()["embeddings"][0]

    # ChromaDB does the similarity search — no manual cosine loop needed
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=12,
        include=["documents", "metadatas", "distances"]
    )

    texts = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    print(f"[RETRIEVAL] raw_candidates={len(texts)}")
    for idx, (meta, dist) in enumerate(zip(metas, distances)):
        source = meta.get("source", "unknown") if isinstance(meta, dict) else "unknown"
        print(f"[RETRIEVAL] cand={idx} source={source} dist={float(dist):.4f}")

    if not texts:
        return {
            "answer": "I don't have relevant information about that in my notes.",
            "confidence": "none",
            "sources": []
        }

    texts, metas, distances = _rerank_results(query, texts, metas, distances, top_k=5)

    # Cosine distance: lower = more similar. Refuse if best match > 0.75
    if distances[0] > 0.75:
        print(f"[CONFIDENCE_GUARD] best_distance={float(distances[0]):.4f} > 0.75, refusing answer")
        return {
            "answer": "I don't have relevant information about that in my notes.",
            "confidence": "none",
            "sources": []
        }

    # Preserve source order while deduplicating.
    sources = list(dict.fromkeys([m["source"] for m in metas]))
    print(f"[CONTEXT] selected_sources={sources}")
    context = "\n\n".join(texts)

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Answer only from provided context. If context has exact values/model names/versions, copy them exactly. Be concise and factual. Respond with ONLY valid JSON: {\"answer\": \"...\", \"confidence\": \"high|medium|low\"}"},
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
