"""A workflow: the CODE decides the steps. Route -> look up -> write -> check -> (retry once)."""
import re, json
from client import client, MODEL
from mona import SYSTEM
from tools import get_order, get_refund

ROUTER = """Classify the customer message. Reply with exactly one word:
refund  - about money back or a refund
status  - about where an order is or when it arrives
other   - anything else"""

def llm(system, messages, max_tokens=300):
    msg = client.messages.create(model=MODEL, max_tokens=max_tokens, system=system,
                                 thinking={"type": "disabled"}, messages=messages)
    return msg.content[0].text.strip()

def route(text):                                   # 1. routing: one small model call
    out = llm(ROUTER, [{"role": "user", "content": text}], max_tokens=10).lower()
    return next((r for r in ("refund", "status") if r in out), "other")

def look_up(text, kind):                           # 2. tools called by CODE, every time
    m = re.search(r"\d{4}", text)
    if not m:
        return {"error": "no order number in the message"}
    oid = int(m.group())
    facts = {"order": get_order(oid)}
    if kind == "refund":
        facts["refund"] = get_refund(oid)
    return facts

ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

def check(reply, facts=None, kind=None, strict=False):    # 4. code checks
    c = {"short":   len(re.findall(r"[.!؟?]", reply)) <= 2 and len(reply) <= 220,       # from L06
         "no_md":   not re.search(r"\*\*|^#|^\s*[-•]", reply, re.M),
         "no_date": not re.search(r"غد[اًا]?|بكر[ةه]|tomorrow|النهارد[هة]", reply)}
    if strict:                                                                      # added after reading v1's replies
        known = json.dumps(facts, ensure_ascii=False)
        c["grounded"] = all(n in known for n in re.findall(r"\d+", reply.translate(ARABIC_DIGITS)))   # every number comes from the facts
        c["on_topic"] = kind == "refund" or not re.search(r"فلوس|المبلغ|الدفع|استرداد|refund", reply)  # status answers don't talk refunds
    return c

def answer(text, strict=False, trace=True):
    kind = route(text)
    facts = look_up(text, kind)
    system = SYSTEM + f"\n<facts>\n{json.dumps(facts, ensure_ascii=False)}\n</facts>"
    messages = [{"role": "user", "content": text}]
    reply = llm(system, messages)                  # 3. write the reply from the facts
    steps = {"route": kind, "facts": facts, "first": reply, "checks": check(reply, facts, kind, strict), "retry": False}
    failed = [k for k, ok in steps["checks"].items() if not ok]
    if failed:                                     # 5. one retry with the failed rules
        steps["retry"] = True
        messages += [{"role": "assistant", "content": reply},
                     {"role": "user", "content": f"Rewrite your reply. It broke these rules: {', '.join(failed)}. "
                                                 "Use only the facts: no numbers, dates or day names that are not in the facts, "
                                                 "answer only what was asked, at most two short sentences."}]
        reply = llm(system, messages)
        steps["checks_after"] = check(reply, facts, kind, strict)
    if trace:
        print(f"  route={kind}  facts={json.dumps(facts, ensure_ascii=False)}")
        if steps["retry"]: print(f"  first draft failed {failed}: {steps['first']!r}")
    return reply, steps

if __name__ == "__main__":
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "طلبي رقم 1043 هيوصل إمتى؟"
    print("Q:", q); r, _ = answer(q, strict=True); print("Mona:", r)
