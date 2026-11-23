import json
from client import client, MODEL

def generate_dataset(n=8):           # let the model write the test cases
    msg = client.messages.create(
        model=MODEL, max_tokens=800, thinking={"type": "disabled"},
        messages=[{"role": "user", "content":
            f"Write {n} different messages that customers send to the support chat of an "
            "Egyptian online store: refunds, late orders, broken products, payment. "
            "Egyptian Arabic, short, like real chat messages. Return a JSON array of strings."},
            {"role": "assistant", "content": "```json"}],
        stop_sequences=["```"])
    return json.loads(msg.content[0].text)

MINE = ["عايز فلوسي ترجع", "الفلوس هترجع إمتى؟", "رجعت المنتج من أسبوع ولسه مفيش فلوس",
        "ينفع ترجعولي الفلوس كاش؟"]                # written by hand: the refund cases we care about

if __name__ == "__main__":
    data = generate_dataset() + MINE
    json.dump(data, open("dataset.json", "w"), ensure_ascii=False, indent=1)
    print(len(data), "cases"); print("\n".join(data))
