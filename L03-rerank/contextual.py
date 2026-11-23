from rerank import client, MODEL
from rag2 import chunks

DOC = open("docs.md").read()

def situate(chunk):                  # Anthropic's Contextual Retrieval prompt
    msg = client.messages.create(
        model=MODEL, max_tokens=150,
        thinking={"type": "disabled"},
        messages=[{"role": "user", "content":
            f"<document>\n{DOC}\n</document>\n"
            "Here is the chunk we want to situate within the whole document\n"
            f"<chunk>\n{chunk}\n</chunk>\n"
            "Please give a short succinct context to situate this chunk "
            "within the overall document for the purposes of improving "
            "search retrieval of the chunk. "
            "Answer only with the succinct context and nothing else."}])
    return msg.content[0].text.strip()

ctx_chunks = [situate(c) + "\n\n" + c for c in chunks]   # index these instead

if __name__ == "__main__":
    print(ctx_chunks[2])                 # the shipping section
