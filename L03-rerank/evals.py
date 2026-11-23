from rag2 import chunks, VectorIndex, BM25Index, hybrid
from rerank import rerank
from contextual import ctx_chunks

EVALS = [  # the customer's question (in Egyptian) -> the section that answers it
    ("عايز فلوسي ترجع", "سياسة الاسترداد"),
    ("الـ error ده بيطلعلي: TS-999", "Error TS-999"),
    ("الأوردر هيوصل إمتى؟", "الشحن والتوصيل"),
    ("المنتج جالي مكسور", "المنتجات التالفة"),
    ("عايز أغير المقاس", "الاستبدال"),
    ("نسيت الباسورد", "الحساب وكلمة المرور"),
    ("ينفع أقسط؟", "طرق الدفع"),
    ("الموبايل بايظ من المصنع", "الضمان"),
    ("بيقولي TS-500", "Error TS-500"),
    ("مش عايز الطلب خلاص", "إلغاء الطلب"),
    ("رقم خدمة العملاء كام؟", "الدعم الفني"),
    ("المنتج مش موجود TS-404", "Error TS-404"),
]
title = lambda i: chunks[i].split("\n")[0]
plain = (VectorIndex(chunks), BM25Index(chunks))
ctx = (VectorIndex(ctx_chunks), BM25Index(ctx_chunks))
runs = {
    "Hybrid":                lambda q: hybrid(q, *plain, k=3),
    "Hybrid + Rerank":       lambda q: rerank(q, hybrid(q, *plain, k=6)),
    "Contextual":            lambda q: hybrid(q, *ctx, k=3),
    "Contextual + Rerank":   lambda q: rerank(q, hybrid(q, *ctx, k=6)),
}
for name, run in runs.items():
    got = [[title(i) for i in run(q)] for q, _ in EVALS]
    top1 = sum(g[:1] == [want] for g, (_, want) in zip(got, EVALS))
    top3 = sum(want in g for g, (_, want) in zip(got, EVALS))
    print(f"{name:20s} top1 {top1:2d}/12   top3 {top3:2d}/12")
