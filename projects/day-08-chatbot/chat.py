import requests
import json

conversation_history = [
    {"role": "system", "content": "You are a distinguished Go engineer..."}
]

while True:
    prompt_input = input("\nYou: ")

    if prompt_input == "quit":
        break

    conversation_history.append({"role" : "user", "content" : prompt_input})

    response = requests.post(
        "http://localhost:11434/api/chat",
        json = {
            "model": "phi3:mini",
            "messages": conversation_history,
            "stream": True
        },
        stream=True
    )

    print("AI: ", end="", flush=True)

    full_response = ""
    for line in response.iter_lines():
        if line:
            # Decode bytes to string and parse json
            chunk = json.loads(line.decode('utf-8'))
            # extract the content otken from the nested message obeject
            token = chunk.get("message", {}).get("content", "")
            # print the token immediately without moving to a new line
            print(token, end="", flush=True)
            # accumulate the complete answer
            full_response += token

    print()

    conversation_history.append({"role": "assistant", "content": full_response})

