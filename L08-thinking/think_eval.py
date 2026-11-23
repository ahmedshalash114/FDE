"""L07's eval again: tools given, NO extra rule in the prompt. Thinking off vs on."""
import json, time
from agent import ask
from mona import SYSTEM
from tools import TOOLS
from db import ORDERS
import importlib; L07 = importlib.import_module("eval_l07")   # QUESTIONS, TRUTH, grade() from L07

MODES = {"thinking off": {"type": "disabled"},
         "thinking on":  {"type": "enabled", "budget_tokens": 2000}}
results = {m: [] for m in MODES}
for oid, q in L07.QUESTIONS:
    truth = L07.TRUTH.get(oid, {"order_id": oid, "error": "order not found"})
    for mode, think in MODES.items():
        t0 = time.time()
        reply, messages = ask(q, tools=TOOLS, system=SYSTEM, thinking=think, trace=False)
        secs = time.time() - t0
        calls = [b.name + str(b.input) for m in messages if m["role"] == "assistant" for b in m["content"] if b.type == "tool_use"]
        thoughts = [b.thinking for m in messages if m["role"] == "assistant" for b in m["content"] if b.type == "thinking"]
        g = L07.grade(q, reply, truth) if reply.strip() else {"reason": "no reply: the model spent the whole budget thinking", "pass": False}   # code check first
        results[mode].append({"q": q, "reply": reply, "calls": calls, "thinking": thoughts, "secs": round(secs, 1), **g})
        print(f"{mode:12s} | {q[:26]:26s} | {'PASS' if g['pass'] else 'FAIL'} | calls {len(calls)} | {reply[:60]!r}")
for mode, rs in results.items():
    print(f"== {mode}: {sum(r['pass'] for r in rs)}/{len(rs)} correct · tool calls in {sum(bool(r['calls']) for r in rs)}/{len(rs)}")
json.dump(results, open("results.json", "w"), ensure_ascii=False, indent=1)
