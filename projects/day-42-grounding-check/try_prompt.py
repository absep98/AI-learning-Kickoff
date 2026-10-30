import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "day-27" / "awesome-project"))
from assistant import groq_client

context = "Temperature adjusts how much randomness the model uses when picking the next token."
query = "how does LoRA fine-tuning work"

response = groq_client.chat.completions.create(
    model="openai/gpt-oss-20b",
    temperature=0,
    messages=[{"role" : "system", "content": "Answer only using the provided context. Be concise Reply with only a JSON object that has two keys, answer and quote. quote must be one sentence copied exactly from the context.  if the context does not contain the answer, return empty strings for both answer and quote."}, {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}],
)

print(response.choices[0].message.content)
