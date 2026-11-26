"""L19's retriever: TF-IDF over character 3-grams. No extra model, works on Egyptian spelling (mostly)."""
import math, re
from .data import POLICY

def _norm(s): return re.sub("ى", "ي", re.sub("ة", "ه", re.sub("[أإآ]", "ا", re.sub("[ً-ْ]", "", s))))
def _grams(s):
    g = {}
    for w in filter(None, re.split(r"[^؀-ۿ0-9]+", _norm(s))):
        p = f" {w} "
        for i in range(len(p) - 2): g[p[i:i + 3]] = g.get(p[i:i + 3], 0) + 1
    return g
_G = [_grams(d) for d in POLICY]
_DF = {}
for g in _G:
    for t in g: _DF[t] = _DF.get(t, 0) + 1
def _vec(g):
    v = {t: c * math.log(1 + len(POLICY) / _DF.get(t, 1)) for t, c in g.items()}; n = math.sqrt(sum(x * x for x in v.values())) or 1
    return {t: x / n for t, x in v.items()}
_V = [_vec(g) for g in _G]

def retrieve(q: str, k: int = 3) -> list[str]:
    qv = _vec(_grams(q))
    scored = sorted(((sum(w * dv.get(t, 0) for t, w in qv.items()), i) for i, dv in enumerate(_V)), reverse=True)
    return [POLICY[i] for _, i in scored[:k]]
