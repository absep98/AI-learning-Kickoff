import json
import re


def parse_answer(raw_text):
    """Returns (answer, quote) if raw_text is a JSON object with two string fields, else None."""
    try:
        d = json.loads(raw_text)
    except json.JSONDecodeError:
        return None

    if not isinstance(d, dict):
        return None

    answer = d.get("answer")
    quote = d.get("quote")
    if not isinstance(answer, str) or not isinstance(quote, str):
        return None

    return (answer, quote)


def normalize(text):
    # Lowercase, then keep only letters/digits separated by single spaces, so markdown
    # (**bold**, backticks), colons and other punctuation can't cause a false rejection.
    text = re.sub(r"[^a-z0-9]+", " ", text.lower())
    return text.strip()


def quote_in_context(quote, context):
    quote = normalize(quote)
    context = normalize(context)

    if quote == "":
        return False

    return quote in context


if __name__ == "__main__":
    context = "Temperature adjusts how much randomness the model uses when picking the next token."

    parse_cases = [
        ('{"answer": "a", "quote": "q"}', ("a", "q")),
        ("Sorry, I can't help with that", None),
        ('{"answer": "hi"}', None),
        ("[1, 2]", None),
        ('{"answer": "a", "quote": 5}', None),
    ]
    for raw, expected in parse_cases:
        print(f"parse_answer({raw!r}) -> {parse_answer(raw)}   expected {expected}")

    quote_cases = [
        ("Temperature adjusts how much randomness", True),
        ("  TEMPERATURE   adjusts how much\nrandomness ", True),
        ("LoRA adds low-rank adapter matrices", False),
        ("", False),
        ("   ", False),
    ]
    for quote, expected in quote_cases:
        print(f"quote_in_context({quote!r}) -> {quote_in_context(quote, context)}   expected {expected}")
