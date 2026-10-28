import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "day-27" / "awesome-project"))
from assistant import retrieve_chunks

questions = [
    # True = should be answered, False = should be refused.
    # In-scope, clear (wording close to the notes)
    ("what is temperature", True),
    ("what is RAG", True),
    ("what are embeddings", True),
    ("what is ChromaDB used for", True),
    ("what cloud api did we use for generation", True),
    ("what is FastAPI", True),
    ("why did the embedding step break when deployed", True),
    # In-scope, vague (wording unlike the notes, topic is covered)
    ("how do I make repeated questions faster", True),      # caching, day 37
    ("why was the first request so slow", True),            # cold start, day 34
    ("how do I track how much the api costs", True),        # cost monitoring, day 36
    ("how do I stop people abusing my endpoint", True),     # rate limiting, day 38
    ("how do I check that my answers are right", True),     # evals, days 16/31
    ("what happened when the embedding provider ran out of credits", True),  # day 38/40
    ("how did I deploy the app", True),                     # render, day 29
    # Out-of-scope, obvious
    ("who won the 2018 World Cup?", False),
    ("how to cook rice?", False),
    ("what is capital of USA?", False),
    # Out-of-scope, near-miss (AI/tech-flavoured but not in the notes)
    ("how does LoRA fine-tuning work", False),
    ("what is the context window of GPT-4", False),
    ("how does Kubernetes scheduling work", False),
    ("how do I write a SQL join", False),
    ("how do React hooks work", False),
    ("how do I train a model from scratch", True)
]

results = []

for text, should_answer in questions:
    distance = retrieve_chunks(text)[2][0]
    results.append((text, should_answer, distance))

for t in [0.25, 0.30, 0.35, 0.40, 0.45]:
 
    false_refusals = 0
    false_answers =  0
    for text, should_answer, distance in results:
        if distance > t and should_answer:
            false_refusals += 1
        if distance <= t and not should_answer:
            false_answers += 1

    print(t, false_refusals, false_answers)