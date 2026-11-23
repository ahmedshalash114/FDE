"""Workflow vs agent on L07's 6 questions. Same model, same grader."""
import json, time
import eval_l07 as L07
from workflow import answer
from agent import ask          # L07 agent: the MODEL decides which tools to call

rows = {"agent": [], "workflow": [], "workflow+checks": []}
for oid, q in L07.QUESTIONS:
    truth = L07.TRUTH.get(oid, {"order_id": oid, "error": "order not found"})
    reply, messages = ask(q, trace=False)
    calls = [b.name for m in messages if m["role"] == "assistant" for b in m["content"] if b.type == "tool_use"]
    rows["agent"].append({"q": q, "reply": reply, "tool_calls": calls, "llm_calls": sum(m["role"] == "assistant" for m in messages)})
    for mode, strict in (("workflow", False), ("workflow+checks", True)):
        reply, steps = answer(q, strict=strict, trace=False)
        rows[mode].append({"q": q, "reply": reply, "llm_calls": 2 + steps["retry"], **steps})
    for mode in rows:
        r = rows[mode][-1]
        g = L07.grade(q, r["reply"], truth) if r["reply"].strip() else {"reason": "no reply", "pass": False}
        r.update(g)
        print(f"{mode:15s} | {q[:26]:26s} | {'PASS' if g['pass'] else 'FAIL'} | {r['reply'][:70]!r}")
for mode, rs in rows.items():
    print(f"== {mode}: grader {sum(r['pass'] for r in rs)}/6 · model calls {sum(r['llm_calls'] for r in rs)} · retries {sum(r.get('retry', False) for r in rs)}")
json.dump(rows, open("results.json", "w"), ensure_ascii=False, indent=1)
