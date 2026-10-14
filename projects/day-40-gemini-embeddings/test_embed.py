import os
from dotenv import load_dotenv
from pathlib import Path
from google.genai import types
from google import genai


REPO_ROOT = Path(os.getenv("REPO_ROOT", r"C:\learning\aithings"))
load_dotenv(REPO_ROOT / ".env")



SENTENCES = ['what is temperature', 'what is embedding']


client = genai.Client()


result = client.models.embed_content(
    model = "gemini-embedding-001",
    contents = SENTENCES,
    config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY", output_dimensionality=768)
)


print(len(result.embeddings))
for e in result.embeddings:
    print(len(e.values))