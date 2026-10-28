


def normalize(text):
    text.lower()
    text.split()
    s = " ".join(text.split())

    return s

def quote_in_context(quote, context):
    quote = normalize(quote)
    context = normalize(context)

    if normalize == "":
        return False

    return quote in context


if __name__ == "__main__":
    context = "Temperature adjusts how much randomness the model uses when picking the next token."