import os
from pathlib import Path
from dotenv import load_dotenv
import time
from google import genai
from google.genai import types
from google.genai import errors
import json
REPO_ROOT = Path(os.getenv("REPO_ROOT", r"C:\learning\aithings"))
load_dotenv(REPO_ROOT / ".env")
OUTPUT_PATH = "./embeddings.json" 

SKIP_FILES = {"day-11-rag-over-notes.md", "day-12-rag-improved.md"}
EMBED_MODEL_NAME = "gemini-embedding-001"
EMBED_DIMENSIONS = 768
BATCH_SIZE = 50
BATCH_PAUSE_SECONDS = 35
MAX_RETRIES = 3

google_api_key = os.getenv("GOOGLE_API_KEY")
genai_client = genai.Client(api_key=google_api_key) if google_api_key else None


def embed(texts, task_type):
    """texts: a string or list of strings. Returns a plain list (or list of lists) of floats."""

        
    results = genai_client.models.embed_content(
        model = EMBED_MODEL_NAME,
        contents = texts,
        config = types.EmbedContentConfig(task_type=task_type, output_dimensionality = EMBED_DIMENSIONS)
    )

    if isinstance(texts, str):
        return results.embeddings[0].values

    lists = [e.values for e in results.embeddings]
    return lists


def _load_note_chunks():
    """Read days/*.md and split into paragraph chunks, same approach as rag_chroma.py."""
    days_folder = REPO_ROOT / "days"
    chunks = []
    for path in days_folder.glob("*.md"):
        if path.name in SKIP_FILES:
            continue
        content = path.read_text(encoding="utf-8")
        paragraphs = content.split("\n\n")
        chunks.extend([(p.strip(), path.name) for p in paragraphs if p.strip() and len(p.strip()) > 80])
    return chunks

def _embed_with_retry(texts, task_type):
    """Retries only temporary failures (5xx or 429 rate limit) with 1s, 2s, 4s backoff."""
    for attempt in range(MAX_RETRIES):
        try:
            return embed(texts, task_type)
        except errors.APIError as err:
            retryable = isinstance(err, errors.ServerError) or err.code == 429
            last = attempt + 1 == MAX_RETRIES
            if not retryable or last:
                raise
            wait = 2 ** attempt
            print(f"[embed] attempt {attempt + 1}/{MAX_RETRIES} failed ({err.code}), retrying in {wait}s")
            time.sleep(wait)




if __name__ == "__main__":
    try:
        chunks = _load_note_chunks()
        texts = [text for text, _ in chunks]
        all_vectors = []
        for start in range(0, len(texts), BATCH_SIZE):
            batch = texts[start : start + BATCH_SIZE]
            vector = _embed_with_retry(batch, "RETRIEVAL_DOCUMENT")
            all_vectors.extend(vector)
            print(f"embedded {len(all_vectors)}/{len(texts)}")
            time.sleep(BATCH_PAUSE_SECONDS)

        print(len(all_vectors), len(all_vectors[0]))
        entries = []
        for (text, source), vector in zip(chunks, all_vectors):
            entries.append({"text" : text, "source": source, "vector": vector})

        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(entries, f)

    except Exception as err:
        raise err