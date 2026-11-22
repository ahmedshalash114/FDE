import re, sys
from rank_bm25 import BM25Okapi

chunks = open("docs.md").read().strip().split("\n\n")
tok = lambda s: re.findall(r"[\w-]+", s.lower())
bm25 = BM25Okapi([tok(c) for c in chunks])

q = sys.argv[1]
scores = bm25.get_scores(tok(q))
print(scores.round(2))
if scores.max() == 0:
    sys.exit("مفيش ولا نتيجة")

best = chunks[scores.argmax()]
print(f"جاوب من ده بس:\n{best}\n\nالسؤال: {q}")
