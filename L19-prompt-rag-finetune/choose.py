"""L19 · Prompt vs RAG vs fine-tuning — the same experiment as choose.js, in Python (qwen3.5:4b on Ollama, thinking off).
  Part 1 · knowledge : 12 questions about Mona Store's own policies -> prompt only / whole policy in the prompt / RAG (top-3 chunks)
  Part 2 · a fact changes : Cairo shipping 45 -> 60 EGP, edit one chunk and ask again (nothing to retrain)
  Part 3 · behaviour : L18's 20 intent messages, instructions only vs + 6 worked examples
    ollama pull qwen3.5:4b
    python choose.py            # writes results.json and prints the table
The policy, questions and examples are read from choose.js so both versions always test the same thing.
"""
import json, math, re, time
import httpx

SRC = open("choose.js", encoding="utf8").read()
block = lambda name: SRC.split(f"const {name} = [", 1)[1].split("\n];", 1)[0] if f"const {name} = [\n" in SRC else SRC.split(f"const {name} = [", 1)[1].split("]];", 1)[0]
strs = lambda s: re.findall(r"'([^']*)'", s)
POLICY = strs(block("POLICY"))
QS = [tuple(strs(l)) for l in block("QS").splitlines() if l.strip().startswith("[")]
SHOTS = [tuple(p) for p in zip(*[iter(strs(SRC.split("const SHOTS = [", 1)[1].split("]];", 1)[0]))] * 2)]
MSGS = json.loads(re.search(r"const MSGS = (\[\[.*?\]\]);", open("../L18-cost-latency/latency.js", encoding="utf8").read()).group(1)) \
    if __import__("os").path.exists("../L18-cost-latency/latency.js") else []
DONT = re.compile(r"(مش عارف|معرفش|لا أعرف|لا اعرف|مش متأكد|غير متأكد|مفيش عندي معلومة|ليس لدي|تواصل مع|راجع الموقع|اتصل ب)")
PERSONA = "You are Mona, the support agent of Mona Store (Egypt). Answer in Egyptian Arabic in one or two short sentences."
SYS = ("Classify the customer message into one intent: status (where is my order), refund (money back, return or exchange an item), "
       "cancel, complaint, other. Reply with the intent word only.")
INTENTS = ["status", "refund", "cancel", "complaint", "other"]
http = httpx.Client(timeout=300)

def norm(s): return re.sub("ى", "ي", re.sub("ة", "ه", re.sub("[أإآ]", "ا", re.sub("[ً-ْ]", "", s))))
def grams(s):
    g = {}
    for w in filter(None, re.split(r"[^؀-ۿ0-9]+", norm(s))):
        p = f" {w} "
        for i in range(len(p) - 2): g[p[i:i + 3]] = g.get(p[i:i + 3], 0) + 1
    return g

def retrieve(q, docs, k=3):
    """TF-IDF over character 3-grams: no extra model, survives ال / و prefixes and Egyptian spelling (mostly — see Q1)."""
    G = [grams(d) for d in docs]; df = {}
    for g in G:
        for t in g: df[t] = df.get(t, 0) + 1
    def vec(g):
        v = {t: c * math.log(1 + len(docs) / df.get(t, 1)) for t, c in g.items()}; n = math.sqrt(sum(x * x for x in v.values())) or 1
        return {t: x / n for t, x in v.items()}
    qv = vec(grams(q)); sc = [(i, sum(qv[t] * dv.get(t, 0) for t in qv)) for i, dv in enumerate(map(vec, G))]
    return [i for i, _ in sorted(sc, key=lambda x: -x[1])[:k]]

def chat(system, user, num_predict=150):
    t0 = time.time()
    r = http.post("http://localhost:11434/api/chat", json={"model": "qwen3.5:4b", "stream": False, "think": False, "options": {"num_predict": num_predict},
                  "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}).json()
    return {"text": r["message"].get("content") or "", "prompt_tokens": r.get("prompt_eval_count"), "out_tokens": r.get("eval_count"), "ms": round((time.time() - t0) * 1000)}

def grade(text, gold): return "correct" if re.search(gold, text) else "dont_know" if DONT.search(text) else "wrong"

def ask(mode, q, gold, policy=POLICY):
    system, ctx = PERSONA, None
    if mode == "stuff": system += "\nAnswer ONLY from the store policy below. If it is not there, say you are not sure.\n\nSTORE POLICY:\n" + "\n".join(policy)
    if mode == "rag":
        ctx = retrieve(q, policy)
        system += "\nAnswer ONLY from the policy excerpts below. If it is not there, say you are not sure.\n\nPOLICY EXCERPTS:\n" + "\n".join(policy[i] for i in ctx)
    r = chat(system, q); return {"mode": mode, "q": q, "result": grade(r["text"], gold), "chunks": ctx, **r}

def intent(msg, few):
    ex = "\n\nExamples:\n" + "\n".join(f"{m} -> {i}" for m, i in SHOTS) if few else ""
    r = chat(SYS + ex, msg, 20); t = r["text"].lower()
    return {"got": next((i for i in INTENTS if i in t), t.strip()), **r}

if __name__ == "__main__":
    chat(PERSONA, "أهلا")   # warm-up
    res = {"knowledge": [ask(m, q, g) for m in ["prompt", "stuff", "rag"] for q, g in QS]}
    NEW = POLICY[:]; NEW[2] = NEW[2].replace("45", "60")
    res["update"] = [ask(m, QS[2][0], "(60|٦٠|ستين)", NEW) for m in ["prompt", "stuff", "rag"]]
    res["behaviour"] = [{"few": few, "msg": m, "gold": g, **(r := intent(m, few)), "ok": r["got"] == g} for few in [False, True] for m, g in MSGS]
    json.dump(res, open("results.json", "w"), ensure_ascii=False, indent=1)
    for m in ["prompt", "stuff", "rag"]:
        rows = [r for r in res["knowledge"] if r["mode"] == m]
        print(f"{m:6} correct {sum(r['result'] == 'correct' for r in rows):2}/12  wrong {sum(r['result'] == 'wrong' for r in rows):2}"
              f"  not sure {sum(r['result'] == 'dont_know' for r in rows):2}  avg prompt tokens {sum(r['prompt_tokens'] for r in rows) / 12:.0f}")
    for r in res["update"]: print("after the change:", r["mode"], r["result"], r["text"][:60])
    for few in [False, True]: print("few-shot" if few else "zero-shot", sum(r["ok"] for r in res["behaviour"] if r["few"] == few), "/ 20")
