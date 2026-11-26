"""One agent that knows everything  vs  an orchestrator + 3 specialist workers + a writer.
Same 10 multi-part customer messages, same model (qwen3.5:4b on Ollama), one real run.
  single : one call, the system prompt holds ALL the data (orders + prices + return policy)
  multi  : orchestrator splits the message into tasks (constrained JSON) -> each task goes to a worker
           that only sees ITS data -> a writer merges the answers into one reply
Score = how many parts of each message the final reply answers with the right number."""
import json, re, sys, httpx
from store import MESSAGES, POLICY
BIG = "--big" in sys.argv     # 5x the data: does one agent still cope?
if BIG: from store import ORDERS_TABLE_BIG as ORDERS_TABLE, CATALOG_TABLE_BIG as CATALOG_TABLE
else:   from store import ORDERS_TABLE, CATALOG_TABLE

MODEL = "qwen3.5:4b"
URL = "http://localhost:11434/api/chat"
STYLE = "Answer in Egyptian Arabic, short. Always write the exact numbers and codes from your data."

def call(system, user, fmt=None, max_tokens=300):
    body = {"model": MODEL, "stream": False, "think": False, "options": {"num_predict": max_tokens},
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    if fmt: body["format"] = fmt
    r = httpx.post(URL, json=body, timeout=300).json()
    return r["message"]["content"], r.get("prompt_eval_count", 0) + r.get("eval_count", 0)

# ---------- single agent: everything in one prompt ----------
SINGLE = f"You are Mona, the support agent of Mona Store (Egypt). {STYLE}\n\n{ORDERS_TABLE}\n\n{CATALOG_TABLE}\n\n{POLICY}"
def single(msg):
    reply, tok = call(SINGLE, msg)
    return {"reply": reply, "calls": 1, "tokens": tok}

# ---------- multi agent ----------
WORKERS = {
    "orders":  f"You answer questions about orders only. {STYLE}\n\n{ORDERS_TABLE}",
    "catalog": f"You answer questions about product prices only. {STYLE}\n\n{CATALOG_TABLE}",
    "returns": f"You answer questions about returns and refunds only. {STYLE}\n\n{POLICY}",
}
PLAN_SCHEMA = {"type": "object", "properties": {"tasks": {"type": "array", "items": {"type": "object", "properties": {
    "agent": {"type": "string", "enum": list(WORKERS)}, "question": {"type": "string"}}, "required": ["agent", "question"]}}},
    "required": ["tasks"]}
ORCH = ("You are the orchestrator of a support team. Split the customer message into separate tasks, ONE task per question, "
        "and send each to the right agent: orders (order status, tracking codes), catalog (prices), returns (returns, refunds, exchanges). "
        "Copy order numbers and product names exactly. Return JSON.")
WRITER = ("You are Mona, the support agent of Mona Store (Egypt). Merge your team's answers into ONE short reply in Egyptian Arabic. "
          "Keep every number and code exactly as given. Do not add anything new.")

def multi(msg):
    plan_raw, tok = call(ORCH, msg, fmt=PLAN_SCHEMA)
    try: tasks = json.loads(plan_raw)["tasks"]
    except Exception: tasks = []
    answers = []
    for t in tasks:
        a, k = call(WORKERS[t["agent"]], t["question"]); tok += k; answers.append({**t, "answer": a})
    team = "\n".join(f"- ({a['agent']}) {a['question']}\n  {a['answer']}" for a in answers)
    reply, k = call(WRITER, f"Customer message:\n{msg}\n\nTeam answers:\n{team}"); tok += k
    return {"reply": reply, "calls": 2 + len(tasks), "tokens": tok, "tasks": answers}

# ---------- grading (code-based, L06) ----------
AR = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
def has(text, gold): return re.search(rf"(?<!\d){gold}(?!\d)", text.translate(AR)) is not None
def score(reply, parts): return [has(reply, g) for _, g in parts]

if __name__ == "__main__":
    out = []
    for msg, parts in MESSAGES:
        s, m = single(msg), multi(msg)
        s["ok"] = score(s["reply"], parts); m["ok"] = score(m["reply"], parts)
        m["ok_before_writer"] = [any(has(t["answer"], g) for t in m["tasks"]) for _, g in parts]
        out.append({"msg": msg, "parts": parts, "single": s, "multi": m})
        print(msg[:40], "| single", s["ok"], "| multi", m["ok"], "| workers", m["ok_before_writer"])
    P = sum(len(r["parts"]) for r in out)
    for k in ("single", "multi"):
        print(f"{k:7s} parts {sum(sum(r[k]['ok']) for r in out)}/{P}   calls {sum(r[k]['calls'] for r in out)}   tokens {sum(r[k]['tokens'] for r in out)}")
    print(f"workers (before writer) {sum(sum(r['multi']['ok_before_writer']) for r in out)}/{P}")
    json.dump(out, open("results_big.json" if BIG else "results.json", "w"), ensure_ascii=False, indent=1)
