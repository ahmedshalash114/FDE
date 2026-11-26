"""Three ways to get JSON out of the model, on the same 20 messages:
  A. prompt  : "reply with JSON only"
  B. prefill : same prompt + the reply starts with "{"  (L04 trick)
  C. schema  : constrained decoding with a JSON schema (Ollama `format`; on Claude: output_config.format)"""
import json, sys, httpx
from client import client, MODEL
from schema import SCHEMA, schema_errors
from messages import MESSAGES

SYSTEM = ("You read one customer message for Mona Store and extract: order_id (integer or null), "
          "intent (one of: status, refund, cancel, complaint, other) and urgent (true/false). "
          "Reply with JSON only, like {\"order_id\": 1042, \"intent\": \"status\", \"urgent\": false}")

SYSTEM_V2 = SYSTEM + """

How to decide (read carefully):
- intent: status = asks where the order is or when it arrives. refund = wants money back, or wants to return or exchange an item.
  cancel = wants to cancel an order. complaint = angry about the service, the courier or an invoice, without asking for a refund.
  other = anything else (questions, changing the address, thanks).
- urgent: true ONLY if the customer needs it today or now (travel, work, "حالاً", "بسرعة"), the item arrived broken,
  or they threaten to escalate. Being upset alone is NOT urgent. A normal question is NOT urgent. Most messages are not urgent.
- order_id: the order number as an integer (convert Arabic digits like ١٠٨٥ to 1085), or null if there is no number."""

def ask_prompt(text):
    msg = client.messages.create(model=MODEL, max_tokens=200, system=SYSTEM, thinking={"type": "disabled"},
                                 messages=[{"role": "user", "content": text}])
    return msg.content[0].text

def ask_prefill(text):
    msg = client.messages.create(model=MODEL, max_tokens=200, system=SYSTEM, thinking={"type": "disabled"},
                                 messages=[{"role": "user", "content": text}, {"role": "assistant", "content": "{"}])
    return "{" + (msg.content[0].text if msg.content else "")

def ask_schema(text):   # constrained decoding: the model can only produce tokens that fit SCHEMA
    r = httpx.post("http://localhost:11434/api/chat", timeout=120, json={
        "model": MODEL, "stream": False, "think": False, "format": SCHEMA,
        "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": text}]})
    return r.json()["message"]["content"]

def grade(raw, gold):
    oid, intent, urgent = gold
    try: d = json.loads(raw)
    except Exception: return {"json": False, "schema": False, "correct": False, "why": "not JSON"}
    errs = schema_errors(d)
    if errs: return {"json": True, "schema": False, "correct": False, "why": ", ".join(errs)}
    ok = d["order_id"] == oid and d["intent"] == intent and d["urgent"] == urgent
    return {"json": True, "schema": True, "correct": ok, "why": "" if ok else f"got {d}"}

def ask_schema_v2(text):   # same constrained decoding + clear definitions for every field
    r = httpx.post("http://localhost:11434/api/chat", timeout=120, json={
        "model": MODEL, "stream": False, "think": False, "format": SCHEMA,
        "messages": [{"role": "system", "content": SYSTEM_V2}, {"role": "user", "content": text}]})
    return r.json()["message"]["content"]

METHODS = {"prompt": ask_prompt, "prefill": ask_prefill, "schema": ask_schema, "schema+rules": ask_schema_v2}

if __name__ == "__main__":
    out = {}
    for name, fn in METHODS.items():
        rows = []
        for text, *gold in MESSAGES:
            raw = fn(text); g = grade(raw, gold)
            rows.append({"message": text, "gold": gold, "raw": raw, **g})
        n = len(rows)
        print(f"{name:8s} valid JSON {sum(r['json'] for r in rows)}/{n}   matches schema {sum(r['schema'] for r in rows)}/{n}   all 3 fields right {sum(r['correct'] for r in rows)}/{n}")
        out[name] = rows
    json.dump(out, open("results.json", "w"), ensure_ascii=False, indent=1)
