import time, requests

def time_requests(question):
    start = time.time()
    response = requests.post("https://repo-assistant-api.onrender.com/ask", json={"text": question})
    elapsed = time.time() - start
    return elapsed, response.json()


if __name__ == "__main__":
    print("--- RAG question: 'what is temperature' ---")
    summation = 0.0
    for i in range(5):
        elapsed, _ = time_requests("what is temperature")
        print(f"call {i+1}: {elapsed:.2f}s")
        summation += elapsed

    print("total time for 5 calls ", summation)
    print("avg ", summation/5)

    print("\n--- Tool question: 'check git status' ---")
    tool_summation = 0.0
    for i in range(5):
        elapsed, _ = time_requests("check git status")
        print(f"call {i+1}: {elapsed:.2f}s")
        tool_summation += elapsed

    print("total time for 5 calls ", tool_summation)
    print("avg ", tool_summation/5)