from anthropic import Anthropic
from rag2 import chunks, VectorIndex, BM25Index, hybrid

# Claude: client = Anthropic()  and  MODEL = "claude-haiku-4-5"
client = Anthropic(base_url="http://localhost:11434",
                   api_key="ollama")
MODEL = "qwen3.5:4b"                 # local, on Ollama

def rerank(q, ids, k=3):             # the LLM re-orders the candidates
    docs = "\n".join(f'<doc id="{i}">\n{chunks[i]}\n</doc>'
                     for i in ids)
    msg = client.messages.create(
        model=MODEL, max_tokens=50,
        thinking={"type": "disabled"},
        messages=[
          {"role": "user", "content": f"{docs}\n\nQuestion: {q}\n"
           f"Return the ids of the {k} docs that best answer"
           " the question, best first, as JSON."},
          {"role": "assistant", "content": '{"ids": ['}],  # prefill
        stop_sequences=["]"])
    got = [int(x) for x in msg.content[0].text.split(",")
           if x.strip().isdigit()]
    got = [i for i in got if i in ids]   # guard: only ids we sent
    return (got + [i for i in ids if i not in got])[:k]

if __name__ == "__main__":
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "رقم خدمة العملاء كام؟"
    vec, bm25 = VectorIndex(chunks), BM25Index(chunks)
    title = lambda i: chunks[i].split("\n")[0]
    cand = hybrid(q, vec, bm25, k=6)
    print("Hybrid  ", [title(i) for i in cand[:3]])
    print("Reranked", [title(i) for i in rerank(q, cand)])
