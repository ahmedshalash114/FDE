"""Prompt caching on Ollama: the same handbook prefix -> the next calls skip re-reading it.
BAD  = the changing part (customer name) at the START of the system prompt -> every call re-reads everything.
GOOD = the changing part at the END -> the handbook prefix is reused."""
import json, sys, time
from client import client, MODEL
from handbook import HANDBOOK

CALLS = [  # (customer, question)
    ("Sara",   "رجّعت سماعة من 4 أيام، الفلوس هترجع إمتى؟"),
    ("Omar",   "عايز أرجّع جاكيت، في رسوم؟"),
    ("Nour",   "هل بتوصلوا يوم الجمعة؟"),
    ("Youssef","الشحن لأسوان بياخد قد إيه؟"),
    ("Mariam", "ينفع حد تاني يستلم الأوردر بدالي؟"),
]

def system_bad(name):  return f"Today is Wednesday 26 Nov 2026. Customer name: {name}.\n\n" + HANDBOOK
def system_good(name): return HANDBOOK + f"\n\nToday is Wednesday 26 Nov 2026. Customer name: {name}."

def body(system, q):
    return dict(model=MODEL, max_tokens=120, system=system, thinking={"type": "disabled"},
                messages=[{"role": "user", "content": q}])

def run(kind):
    sysf = system_bad if kind == "bad" else system_good
    rows = []
    for name, q in CALLS:
        t0 = time.perf_counter()
        msg = client.messages.create(**body(sysf(name), q))
        rows.append({"kind": kind, "customer": name, "q": q, "ms": round((time.perf_counter() - t0) * 1000),
                     "input_tokens": msg.usage.input_tokens, "reply": msg.content[0].text})
        print(f"{kind:4s} {name:8s} {rows[-1]['ms']:6d} ms  in={msg.usage.input_tokens}  {rows[-1]['reply'][:60]}")
    return rows

if __name__ == "__main__":
    if "--dump" in sys.argv:   # the exact request bodies, in order (used to run them on the Mac)
        json.dump([body(system_bad(n), q) for n, q in CALLS] + [body(system_good(n), q) for n, q in CALLS],
                  open("requests.json", "w"), ensure_ascii=False); sys.exit()
    bad = run("bad"); good = run("good")
    for k, rows in (("bad", bad), ("good", good)):
        print(k, "total", sum(r["ms"] for r in rows), "ms")
