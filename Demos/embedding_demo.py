import requests
import math

# --- Step 2: Embedding — turning text into meaning-vectors ---
# Using Ollama locally (no API key needed!)

OLLAMA_URL = "http://localhost:11434/api/embed"
MODEL = "all-minilm"  # dedicated embedding model (not a chat model)

texts = [
    "cat",
    "kitten",
    "dog",
    "car",
    "automobile",
    "python programming language",
]

print("=" * 60)
print("STEP 2: EMBEDDING — Text becomes numbers (vectors)")
print("=" * 60)
print(f"Using local model: {MODEL} via Ollama\n")

# Get embeddings for all texts
embeddings = {}
for text in texts:
    resp = requests.post(OLLAMA_URL, json={"model": MODEL, "input": text})
    vector = resp.json()["embeddings"][0]
    embeddings[text] = vector
    # Show first 5 dimensions
    print(f'"{text}"')
    print(f"  Vector length: {len(vector)} dimensions")
    print(f"  First 5 values: [{', '.join(f'{v:.4f}' for v in vector[:5])}...]")
    print()


# --- Cosine Similarity: prove similar meaning = close vectors ---

def cosine_similarity(vec_a, vec_b):
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))
    return dot / (mag_a * mag_b)


print("=" * 60)
print("COSINE SIMILARITY — Does meaning = closeness?")
print("=" * 60)

pairs = [
    ("cat", "kitten"),         # very similar meaning
    ("cat", "dog"),            # related (both animals)
    ("car", "automobile"),     # same meaning, different word
    ("cat", "car"),            # unrelated
    ("cat", "python programming language"),  # totally unrelated
]

for word_a, word_b in pairs:
    sim = cosine_similarity(embeddings[word_a], embeddings[word_b])
    bar = "█" * int(sim * 30)
    print(f'  "{word_a}" vs "{word_b}"')
    print(f"  Similarity: {sim:.4f}  {bar}")
    print()
