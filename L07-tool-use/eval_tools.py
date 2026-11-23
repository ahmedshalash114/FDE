"""Same questions, with and without tools. The grader from L06 checks every reply against the database."""
import json
from client import client, MODEL
from agent import ask
from mona import SYSTEM, SYSTEM_TOOLS
from tools import TOOLS
from db import ORDERS

QUESTIONS = [
    (1042, "الأوردر 1042 وصل فين؟"),
    (1043, "طلبي رقم 1043 هيوصل إمتى؟"),
    (1044, "هو أوردر 1044 اتشحن ولا لسه؟"),
    (1045, "رجّعت الأوردر 1045، فلوسي فين؟"),
    (1046, "لغيت أوردر 1046، الفلوس رجعت؟"),
    (1047, "عايز أعرف حالة أوردر 1047"),
]
TRUTH = {o[0]: dict(zip(["order_id", "item", "status", "eta", "refund"], o)) for o in ORDERS}

def grade(question, reply, truth):
    out = client.messages.create(
        model=MODEL, max_tokens=200, thinking={"type": "disabled"},
        messages=[{"role": "user", "content": f"""<database>{json.dumps(truth, ensure_ascii=False)}</database>
<question>{question}</question>
<reply>{reply}</reply>
Does the reply match the database, with no invented status, date or promise?
Answer as JSON: {{"reason": "<one sentence>", "pass": true or false}}"""},
            {"role": "assistant", "content": "```json"}],
        stop_sequences=["```"])
    return json.loads(out.content[0].text)

MODES = {"no_tools": (None, SYSTEM), "tools": (TOOLS, SYSTEM), "tools+rule": (TOOLS, SYSTEM_TOOLS)}
results = {m: [] for m in MODES}
for oid, q in QUESTIONS:
    truth = TRUTH.get(oid, {"order_id": oid, "error": "order not found"})
    for mode, (tools, system) in MODES.items():
        reply, messages = ask(q, tools=tools, system=system, trace=False)
        calls = [b.name + str(b.input) for m in messages if m["role"] == "assistant" for b in m["content"] if b.type == "tool_use"]
        g = grade(q, reply, truth)
        results[mode].append({"q": q, "reply": reply, "calls": calls, **g})
        print(f"{mode:10s} | {q[:28]:28s} | {'PASS' if g['pass'] else 'FAIL'} | calls {calls} | {reply[:70]!r}")
for mode, rs in results.items():
    print(f"== {mode}: {sum(r['pass'] for r in rs)}/{len(rs)} match the database · tool calls in {sum(bool(r['calls']) for r in rs)}/{len(rs)}")
json.dump(results, open("results.json", "w"), ensure_ascii=False, indent=1)
