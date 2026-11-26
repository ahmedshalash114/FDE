"""Memory, three ways, for a customer who comes back the next day:
  none    : a new conversation, nothing from yesterday
  history : send yesterday's whole conversation again (works, but the prompt keeps growing)
  memory  : after each conversation, extract a small JSON memory (L12: schema), save it, and load it next time"""
import json, os, sys, httpx
from client import client, MODEL
from customers import CUSTOMERS, ASKS_AGAIN

SYSTEM = ("You are Mona, the support agent of Mona Store (Egypt). Answer in Egyptian Arabic, in at most two short sentences. "
          "Use what you know about the customer; do not ask for information they already gave.")
MEM_SCHEMA = {"type": "object", "properties": {
    "name": {"type": ["string", "null"]}, "order_ids": {"type": "array", "items": {"type": "integer"}},
    "city": {"type": ["string", "null"]}, "contact": {"type": ["string", "null"]},
    "payment": {"type": ["string", "null"]}, "notes": {"type": "array", "items": {"type": "string"}}},
    "required": ["name", "order_ids", "city", "contact", "payment", "notes"], "additionalProperties": False}
MEM_DIR = "memories"

def chat(messages, system=SYSTEM):
    msg = client.messages.create(model=MODEL, max_tokens=150, system=system, thinking={"type": "disabled"}, messages=messages)
    return (msg.content[0].text if msg.content else ""), msg.usage.input_tokens

def session1(c):
    msgs = []
    for u in c["s1"]:
        msgs.append({"role": "user", "content": u}); r, _ = chat(msgs); msgs.append({"role": "assistant", "content": r})
    return msgs

def extract_memory(msgs, customer_only=True):   # constrained JSON (Ollama `format`); on Claude: output_config.format, or the memory tool
    # v1 (customer_only=False) read the whole chat -> it saved Mona's own made-up promises as "facts"
    convo = "\n".join(f"{m['role']}: {m['content']}" for m in msgs if m["role"] == "user" or not customer_only)
    r = httpx.post("http://localhost:11434/api/chat", timeout=120, json={"model": MODEL, "stream": False, "think": False, "format": MEM_SCHEMA,
        "messages": [{"role": "system", "content": "Extract what we should remember about this customer for next time. Facts only, from the customer's own words. Keep notes short (preferences, constraints)."},
                     {"role": "user", "content": convo}]})
    return json.loads(r.json()["message"]["content"])

def render(mem):   # readable lines instead of raw JSON
    lines = [f"- {k}: {', '.join(map(str, v)) if isinstance(v, list) else v}" for k, v in mem.items() if v not in (None, "", [])]
    return "What this customer told us before (use it, don't ask again):\n" + "\n".join(lines)

def save(name, mem): os.makedirs(MEM_DIR, exist_ok=True); json.dump(mem, open(f"{MEM_DIR}/{name}.json", "w"), ensure_ascii=False, indent=1)
def load(name): return json.load(open(f"{MEM_DIR}/{name}.json"))

def session2(c, mode, history, mem_v1=None):
    q = {"role": "user", "content": c["s2"]}
    if mode == "none":      return chat([q])
    if mode == "history":   return chat(history + [q])
    if mode == "memory_v1": return chat([q], system=SYSTEM + "\n\n<memory>\n" + json.dumps(mem_v1, ensure_ascii=False) + "\n</memory>")
    return chat([q], system=SYSTEM + "\n\n<memory>\n" + render(load(c["name"])) + "\n</memory>")

def remembered(reply, c): return any(w in reply for w in c["expect"]) and not any(a in reply for a in ASKS_AGAIN)

MODES = ("none", "history", "memory_v1", "memory")

if __name__ == "__main__":
    out = {"customers": []}
    for c in CUSTOMERS:
        hist = session1(c); mem_v1 = extract_memory(hist, customer_only=False); mem = extract_memory(hist); save(c["name"], mem)
        row = {"name": c["name"], "session1": hist, "memory_v1": mem_v1, "memory": mem, "today": c["s2"], "modes": {}}
        for mode in MODES:
            reply, tokens = session2(c, mode, hist, mem_v1)
            row["modes"][mode] = {"reply": reply, "input_tokens": tokens, "remembered": remembered(reply, c)}
        out["customers"].append(row)
        print(c["name"], mem)
        for m, v in row["modes"].items(): print(f"   {m:8s} {'✓' if v['remembered'] else '✗'} in={v['input_tokens']:4d}  {v['reply'][:70]}")
    for m in MODES:
        rs = [r["modes"][m] for r in out["customers"]]
        print(f"{m:8s} remembered {sum(v['remembered'] for v in rs)}/5   avg input tokens {sum(v['input_tokens'] for v in rs)/5:.0f}")
    json.dump(out, open("results.json", "w"), ensure_ascii=False, indent=1)
