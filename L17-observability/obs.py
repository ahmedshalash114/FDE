"""Observability for Mona: every call becomes a trace (one JSON line), and cheap checks run on every trace.
The point: all 20 calls return HTTP 200 — you only see what's wrong if you log and look.

  traces_v1.jsonl : Mona's current prompt          traces_v2.jsonl : the prompt fixed using what the traces showed
Checks per trace (plain code, no extra model calls):
  fusha     : the reply reads like Modern Standard Arabic instead of Egyptian (word lists, rough but useful)
  too_long  : more than 2 sentences / 60 words (the spec says 2 short sentences)
  promise   : promises a time or an amount we never gave it ("خلال 24 ساعة", "3 أيام")
  slow      : took more than 3 s
qwen3.5:4b on Ollama, one real run."""
import json, re, time, uuid, httpx, statistics
from messages import MESSAGES

MODEL, URL = "qwen3.5:4b", "http://localhost:11434/api/chat"
PROMPTS = {
    "v1": "You are Mona, the support agent of Mona Store (Egypt). Answer the customer in Egyptian Arabic, in at most two short sentences.",
    "v2": ("You are Mona, the support agent of Mona Store (Egypt).\n"
           "- Write the way Egyptians text: Egyptian dialect (عامية), NOT فصحى. Use words like: ده، دي، عشان، إزاي، مش، هنـ، حالاً، بتاع.\n"
           "- Never use: سوف، لكن، هذا، هذه، الذي، التي، لديك، يمكنك، نأسف.\n"
           "- At most two short sentences.\n"
           "- Never promise a time, a date or an amount. Say a colleague will check and get back to them.\n"
           "Example: «معلش جداً على التأخير، هراجع الأوردر 1042 وأرد عليك حالاً.»"),
}
FUSHA = {"سوف", "لكن", "هذا", "هذه", "الذي", "التي", "لديك", "يمكنك", "يمكنني", "نأسف", "عزيزي", "سيتم", "نود", "إذا", "حيث", "لقد", "ليس",
         "أيضاً", "أيضا", "هل", "نعم", "ترغب", "تود", "نتمنى", "لنضمن", "مرحباً", "سنقوم", "سأقوم"}
MASRI = {"ده", "دي", "عشان", "إزاي", "ازاي", "مش", "حالاً", "حالا", "بتاع", "بتاعك", "كده", "اللي", "معلش", "خلاص", "دلوقتي", "عايز", "بس", "لسه", "أكيد"}
def is_fusha_word(x): return x in FUSHA or (len(x) >= 4 and x[:2] in ("سأ", "سن", "ست") and x not in ("ستة", "سنة"))       # سأرسل، سنقوم، ستصلك
def is_masri_word(x): return x in MASRI or (len(x) >= 4 and x[:2] in ("هر", "هن", "هت", "هب", "هي") and x not in ("هناك", "هيا"))  # هراجع، هنرجع، هتوصل

def checks(reply, ms):
    w = re.findall(r"[\w\u0600-\u06FF]+", reply)
    f, m = sum(map(is_fusha_word, w)), sum(map(is_masri_word, w))
    sentences = [s for s in re.split(r"[.!؟?\n]+", reply) if len(s.split()) >= 3]          # "أهلاً بك!" alone is not a sentence
    return {"fusha": f > m, "too_long": len(sentences) > 2 or len(w) > 60,
            "promise": bool(re.search(r"(\d+|[٠-٩]+)\s*(ساع|يوم|أيام|ايام|دقيق|أسبوع)|خلال\s+(اليوم|يوم|يومين|ساع|أسبوع|\d)|النهارده|بكرة|بكره", reply)),
            "slow": ms > 3000}

def traced(version, msg):
    t0 = time.time()
    r = httpx.post(URL, timeout=300, json={"model": MODEL, "stream": False, "think": False, "options": {"num_predict": 200},
        "messages": [{"role": "system", "content": PROMPTS[version]}, {"role": "user", "content": msg}]}).json()
    reply = r["message"]["content"]
    ms = round(r.get("total_duration", (time.time() - t0) * 1e9) / 1e6)   # Ollama reports its own timing
    trace = {"trace_id": uuid.uuid5(uuid.NAMESPACE_URL, version + msg).hex[:12], "version": version, "model": MODEL, "input": msg, "output": reply,
             "prompt_tokens": r.get("prompt_eval_count"), "output_tokens": r.get("eval_count"), "ms": ms, "status": "ok" if reply else "empty"}
    trace["checks"] = checks(reply, ms)
    return trace

def dashboard(tr):
    n = len(tr); ms = sorted(t["ms"] for t in tr)
    d = {"calls": n, "http_ok": sum(t["status"] == "ok" for t in tr), "p50_ms": ms[n // 2], "p95_ms": ms[min(n - 1, int(n * 0.95))],
         "avg_output_tokens": round(statistics.mean(t["output_tokens"] or 0 for t in tr))}
    for k in ("fusha", "too_long", "promise", "slow"): d[k] = sum(t["checks"][k] for t in tr)
    d["clean"] = sum(not any(t["checks"].values()) for t in tr)
    return d

if __name__ == "__main__":
    out = {}
    for v in PROMPTS:
        tr = [traced(v, m[0]) for m in MESSAGES]
        with open(f"traces_{v}.jsonl", "w") as f:
            for t in tr: f.write(json.dumps(t, ensure_ascii=False) + "\n")
        out[v] = dashboard(tr); print(v, out[v])
    json.dump(out, open("dashboard.json", "w"), indent=1)
