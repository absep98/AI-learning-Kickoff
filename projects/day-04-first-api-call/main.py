import os
from google import genai

# -------------------------------------------------------
# STEP 1: Load API key from environment variable
# Never hardcode your API key in the file.
# Set it first in your terminal:
#   $env:GEMINI_API_KEY = "your-key-here"
# -------------------------------------------------------
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise EnvironmentError(
        "GEMINI_API_KEY environment variable not set.\n"
        "Run this in your terminal first:\n"
        '  $env:GEMINI_API_KEY = "your-key-here"'
    )

# -------------------------------------------------------
# STEP 2: Create the client
# -------------------------------------------------------
client = genai.Client(api_key=api_key)

# -------------------------------------------------------
# STEP 3: Send a plain prompt and print the response
# Model: gemini-2.0-flash  (free tier, fast, capable)
# -------------------------------------------------------
print("--- PLAIN PROMPT ---")
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Explain what a context window is in one paragraph, like I'm a software engineer new to AI.",
)
print(response.text)

# -------------------------------------------------------
# STEP 4: Check token usage
# -------------------------------------------------------
print("\n--- TOKEN USAGE ---")
print(f"Input tokens:  {response.usage_metadata.prompt_token_count}")
print(f"Output tokens: {response.usage_metadata.candidates_token_count}")
print(f"Total tokens:  {response.usage_metadata.total_token_count}")

# Gemini 2.0 Flash free tier = $0 (rate limited but free)
# Paid tier: ~$0.10 per 1M input tokens, ~$0.40 per 1M output tokens
cost_estimate = (
    response.usage_metadata.prompt_token_count * 0.10 / 1_000_000
    + response.usage_metadata.candidates_token_count * 0.40 / 1_000_000
)
print(f"Estimated cost (if on paid tier): ${cost_estimate:.6f}")

# -------------------------------------------------------
# STEP 5: System prompt — change the model's personality
# -------------------------------------------------------
print("\n--- WITH SYSTEM PROMPT ---")
response2 = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="What is temperature in LLMs?",
    config={
        "system_instruction": "You are a no-nonsense senior engineer. Answer in 2 bullet points max. No fluff.",
        "temperature": 0.3,
    },
)
print(response2.text)

# -------------------------------------------------------
# STEP 6: Structured JSON output
# Ask the model to return data in a specific format
# -------------------------------------------------------
print("\n--- STRUCTURED JSON OUTPUT ---")
response3 = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=(
        "List 3 things LLMs are good at and 3 things they are bad at. "
        "Return ONLY valid JSON in this exact format, no extra text:\n"
        '{"good_at": ["...", "...", "..."], "bad_at": ["...", "...", "..."]}'
    ),
    config={"temperature": 0.1},
)
print(response3.text)
