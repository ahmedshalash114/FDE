"""Questions, database truth and the grader from L07."""
import json
from client import client, MODEL
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
