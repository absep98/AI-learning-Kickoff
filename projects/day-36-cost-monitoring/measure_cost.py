import requests

URL = "https://repo-assistant-api.onrender.com/ask"


def ask(question):
    response = requests.post(URL, json={"text": question})
    return response.json()


def run_batch(label, question, n=5):
    print(f"--- {label}: '{question}' ---")
    total_cost = 0.0
    total_tokens = 0
    for i in range(n):
        data = ask(question)
        cost = data.get("total_cost_usd", 0.0)
        tokens = sum(u["total_tokens"] for u in data.get("usage", []))
        print(f"call {i+1}: {tokens} tokens, ${cost:.6f} ({len(data.get('usage', []))} model call(s))")
        total_cost += cost
        total_tokens += tokens

    print(f"avg tokens: {total_tokens/n:.0f}, avg cost: ${total_cost/n:.6f}")
    print(f"projected cost per 1000 requests: ${(total_cost/n)*1000:.2f}\n")


if __name__ == "__main__":
    run_batch("RAG question", "what is temperature")
    run_batch("Tool question", "check git status")
