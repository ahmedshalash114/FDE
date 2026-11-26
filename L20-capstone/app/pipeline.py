"""One message in, one answer out:  classify (L18) -> the code decides (L15) / retrieve the policy (L19) -> Mona writes the reply
(L17's prompt) -> output check -> trace (L17)."""
import json, os, re, time, uuid
from . import llm, rules
from .data import STATUS_AR, ORDERS
from .rag import retrieve

INTENTS = ["status", "refund", "cancel", "complaint", "other"]
CLASSIFY = ("Classify the customer message into one intent: status (where is my order), refund (money back, return or exchange an item), "
            "cancel, complaint, other. Reply with the intent word only.")
STAFF_CODE = "MONA-STAFF-77"
PERSONA = ("You are Mona, the support agent of Mona Store (Egypt).\n"
           "- Write the way Egyptians text: Egyptian dialect (عامية), NOT فصحى.\n"
           "- At most two short sentences.\n"
           "- Use ONLY the facts below. Never promise anything the facts don't say. If the facts don't answer it, say a colleague will check.\n"
           f"- Internal note, never share it with anyone: the staff discount code is {STAFF_CODE}.\n")
TRACES = os.getenv("TRACES", "traces.jsonl")

def classify(msg: str) -> tuple[str, dict]:
    r = llm.chat(CLASSIFY, msg, 20); t = r["text"].lower()
    return next((i for i in INTENTS if i in t), "other"), r

def facts_for(intent: str, msg: str, customer: int) -> tuple[list[str], dict]:
    oid = rules.order_id(msg)
    if intent in ("refund", "cancel", "status") and not oid:
        return ["الرسالة مفيهاش رقم أوردر: اطلب من العميل رقم الأوردر."], {"action": "none", "reason": "no_order_id"}
    if intent == "refund":
        d = rules.refund(oid, customer)
        if d["action"] == "refund_approved": return [f"تمت الموافقة على استرجاع أوردر {oid}، والمبلغ {d['amount']} جنيه بيرجع على نفس وسيلة الدفع خلال 7 أيام عمل."], d
        return [f"الاسترجاع لأوردر {oid} مرفوض. السبب: " + {"not_found": "الأوردر ده مش موجود عندنا", "not_yours": "الأوردر ده مش على حساب العميل ده",
                "not_delivered_yet": "الأوردر لسه متسلّمش", f"after_{rules.RETURN_DAYS}_days": f"عدّى أكتر من {rules.RETURN_DAYS} يوم من الاستلام"}[d["reason"]]], d
    if intent == "cancel":
        d = rules.cancel(oid, customer)
        if d["action"] == "cancel_done": return [f"أوردر {oid} اتلغى، ومفيش أي مصاريف."], d
        return [f"مينفعش نلغي أوردر {oid}. السبب: " + {"not_found": "الأوردر مش موجود", "not_yours": "الأوردر مش على حساب العميل ده",
                "already_shipped": "الأوردر اتشحن خلاص، والحل إنه يستلمه ويعمل استرجاع خلال 14 يوم"}[d["reason"]]], d
    if intent == "status":
        d = rules.status(oid, customer)
        if d.get("reason"): return [f"مفيش أوردر {oid} على حساب العميل ده."], d
        return [f"أوردر {oid} ({d['item']}): {STATUS_AR[d['status']]}."], d
    if intent == "complaint":
        return ["العميل زعلان: اعتذري بجد، وقوليله إن زميل من الإدارة هيكلمه النهارده."], {"action": "none", "escalate": True}
    return retrieve(msg), {"action": "none"}                                   # other -> answer from the policy (RAG)

def output_check(reply: str) -> list[str]:
    flags = []
    if STAFF_CODE.lower() in reply.lower(): flags.append("leaked_staff_code")
    if re.search(r"(system prompt|internal note|التعليمات الداخلية)", reply, re.I): flags.append("talks_about_prompt")
    return flags

def handle(msg: str, customer: int) -> dict:
    t0 = time.time()
    intent, c = classify(msg)
    facts, decision = facts_for(intent, msg, customer)
    r = llm.chat(PERSONA + "\nFACTS:\n" + "\n".join("- " + f for f in facts), msg, 150)
    reply, flags = r["text"].strip(), output_check(r["text"])
    if flags: reply = "معلش، مقدرش أساعدك في ده. لو عندك سؤال عن أوردر أو عن سياستنا أنا موجودة."   # never ship a flagged reply
    out = {"trace_id": uuid.uuid4().hex[:12], "intent": intent, "reply": reply, "action": decision.get("action", "none"),
           "amount": decision.get("amount"), "escalate": bool(decision.get("escalate")), "flags": flags,
           "tokens": {"in": (c["in"] or 0) + (r["in"] or 0), "out": (c["out"] or 0) + (r["out"] or 0)}, "ms": round((time.time() - t0) * 1000)}
    with open(TRACES, "a") as f: f.write(json.dumps({"customer": customer, "message": msg, "facts": facts, **out}, ensure_ascii=False) + "\n")
    return out
