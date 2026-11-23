import re, ollama, numpy as np
from rank_bm25 import BM25Okapi

def embed(texts):                     # bge-m3 on Ollama
    out = ollama.embed(model="bge-m3", input=texts)
    return np.array(out["embeddings"])  # normalized

class VectorIndex:                    # search by meaning
    def __init__(self, chunks):
        self.vecs = embed(chunks)
    def search(self, q, k=3):
        sims = self.vecs @ embed([q])[0]   # cosine
        top = sims.argsort()[::-1][:k]
        return [(int(i), round(float(sims[i]), 2)) for i in top]

class BM25Index:                      # search by the exact word
    def __init__(self, chunks):
        self.tok = lambda s: re.findall(r"[\w-]+", s.lower())
        self.bm25 = BM25Okapi([self.tok(c) for c in chunks])
    def search(self, q, k=3):
        s = self.bm25.get_scores(self.tok(q))
        top = s.argsort()[::-1][:k]
        return [(int(i), round(float(s[i]), 2)) for i in top if s[i] > 0]

def hybrid(q, *indexes, k=3):         # Reciprocal Rank Fusion
    score = {}
    for idx in indexes:
        for rank, (i, _) in enumerate(idx.search(q, k=12)):
            score[i] = score.get(i, 0) + 1 / (60 + rank + 1)
    return sorted(score, key=score.get, reverse=True)[:k]

parts = re.split(r"(?m)^## ", open("docs.md").read())
chunks = [c.strip() for c in parts if c.strip()]

if __name__ == "__main__":
    import sys
    q = sys.argv[1]
    vec, bm25 = VectorIndex(chunks), BM25Index(chunks)
    name = lambda i: chunks[i].split("\n")[0]
    print("BM25       ", [(name(i), s) for i, s in bm25.search(q)] or "مفيش ولا نتيجة")
    print("Embeddings ", [(name(i), s) for i, s in vec.search(q)])
    print("Hybrid     ", [name(i) for i in hybrid(q, vec, bm25)])
