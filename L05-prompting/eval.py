from client import client, MODEL
from prompts import V1, V2, V3, V4

TESTS = [  # the 12 questions from L02, now with the label we expect
    ("عايز فلوسي ترجع", "refund"), ("الـ error ده بيطلعلي: TS-999", "error"),
    ("الأوردر هيوصل إمتى؟", "shipping"), ("المنتج جالي مكسور", "damaged"),
    ("عايز أغير المقاس", "exchange"), ("نسيت الباسورد", "account"),
    ("ينفع أقسط؟", "payment"), ("الموبايل بايظ من المصنع", "warranty"),
    ("بيقولي TS-500", "error"), ("مش عايز الطلب خلاص", "cancel"),
    ("رقم خدمة العملاء كام؟", "support"), ("المنتج مش موجود TS-404", "error"),
]

def classify(prompt, msg):
    out = client.messages.create(
        model=MODEL, max_tokens=60, thinking={"type": "disabled"},
        messages=[{"role": "user", "content": prompt.format(msg=msg)}])
    return out.content[0].text.strip().lower()

for name, prompt in [("V1 vague", V1), ("V2 clear", V2), ("V3 + XML", V3), ("V4 + examples", V4)]:
    got = [classify(prompt, msg) for msg, _ in TESTS]
    score = sum(g == want for g, (_, want) in zip(got, TESTS))
    print(f"{name:14s} {score:2d}/12   e.g. {got[0][:40]!r}")
