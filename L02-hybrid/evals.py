from rag2 import chunks, VectorIndex, BM25Index, hybrid

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
vec, bm25 = VectorIndex(chunks), BM25Index(chunks)
title = lambda i: chunks[i].split("\n")[0]
runs = {"BM25": lambda q, k: [i for i, _ in bm25.search(q, k)],
        "Embeddings": lambda q, k: [i for i, _ in vec.search(q, k)],
        "Hybrid": lambda q, k: hybrid(q, vec, bm25, k=k)}
for k in (1, 3):
    print(f"right section in the top {k}:")
    for name, run in runs.items():
        hits = sum(want in [title(i) for i in run(q, k)] for q, want in EVALS)
        print(f"  {name:11s} {hits}/{len(EVALS)}")
