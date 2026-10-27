from assistant import retrieve_chunks


if __name__ == "__main__":
    in_scope = ["what is RAG", "why batch embeddings requests", "what is prompt injection", "what does cosine distance mean", "how do i stop a rate limit error"]
    out_scope = ["who won the 2018 World Cup", "how do I cook pasta", "capital of Australia", "how to fix a leaking tap", "how does Kubernetes scheduling work"]
    

    for query in in_scope:
        print(retrieve_chunks(query)[2][0])

    for query in out_scope:
        print(retrieve_chunks(query)[2][0])