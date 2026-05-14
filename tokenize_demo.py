import tiktoken

enc = tiktoken.get_encoding("cl100k_base")  # GPT-4 tokenizer

# --- Step 1: Tokenize ---
examples = [
    "The cat sat",
    "The cat sat on the mat",
    "unhappiness",
    "def getUserById(id):",
    "I'm learning AI from scratch!",
]

for text in examples:
    tokens = enc.encode(text)
    pieces = [enc.decode([t]) for t in tokens]
    print(f'"{text}"')
    print(f"  Token count: {len(tokens)}")
    print(f"  Token IDs:   {tokens}")
    print(f"  Pieces:      {pieces}")
    print()

# --- Word vs token comparison ---
print("=" * 50)
print("WORD COUNT vs TOKEN COUNT")
print("=" * 50)
sentences = [
    "Hello world",
    "The quick brown fox jumps over the lazy dog",
    "def calculate_average(numbers: list[int]) -> float:",
    "मैं AI सीख रहा हूं",  # Hindi
]
for s in sentences:
    words = len(s.split())
    tokens = len(enc.encode(s))
    ratio = tokens / words
    print(f'"{s}"')
    print(f"  Words: {words}, Tokens: {tokens}, Ratio: {ratio:.2f} tokens/word")
    print()
