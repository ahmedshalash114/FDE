# L01 · RAG — أصغر RAG في 12 سطر

الكود بتاع الـ LIVE DEMO في الدرس الأول من سلسلة **FDE Academy**.

بيبني index بالـ **BM25** على `docs.md` (8 فقرات لمتجر صغير: الاسترداد، الشحن، الدفع، أكواد الأخطاء...)،
ويجيب أقرب فقرة للسؤال ويحطها في الـ prompt اللي هيروح لـ Claude.

## شغّله

```bash
pip install -r requirements.txt
python rag.py "الـ error ده بيطلعلي: TS-999"
python rag.py "عايز فلوسي ترجع"
```

## النتيجة (حقيقية)

**السؤال الأول** — `TS-999` كلمة نادرة (في doc واحد من 8)، فوزنها عالي، و `error` موجودة في 4 من 8 فوزنها صفر:

```
[0.   0.   0.   0.   0.   1.58 0.   0.  ]
جاوب من ده بس:
Error TS-999: انتهت صلاحية جلسة الدخول، سجّل الخروج ثم ادخل مرة أخرى.

السؤال: الـ error ده بيطلعلي: TS-999
```

**السؤال التاني** — مافيش ولا كلمة مشتركة مع فقرة الاسترداد:

```
[0. 0. 0. 0. 0. 0. 0. 0.]
مفيش ولا نتيجة
```

وده بالظبط ليه محتاجين **Embeddings** جنب الـ BM25 (Hybrid Search) — وده الدرس الجاي.

## Further reading
- Anthropic Academy — [Building with the Claude API](https://anthropic.skilljar.com/claude-with-the-anthropic-api)
- Anthropic — [Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)
