# L02 · Embeddings + Hybrid Search — بإيدينا، وبنقيس

الكود بتاع الدرس التاني من سلسلة **FDE Academy**، ماشي على عناوين Anthropic Academy:
*Text embeddings → Implementing the RAG flow → BM25 lexical search → A Multi-Index RAG pipeline*.

- `VectorIndex`: بحث بالمعنى بـ **bge-m3** (ببلاش، على جهازك بـ Ollama). الكورس بيستخدم Voyage AI، لأن Anthropic مبتعملش embedding models.
- `BM25Index`: بحث بالكلمة نفسها.
- `hybrid()`: بيدمج الاتنين بـ **Reciprocal Rank Fusion**، يعني بالترتيب مش بالـ scores: `1 / (60 + rank)`.
- `evals.py`: 12 سؤال بالمصري، ولكل سؤال الفقرة الصح.

## شغّله

```bash
ollama pull bge-m3
pip install -r requirements.txt
python rag2.py "عايز فلوسي ترجع"
python evals.py
```

## النتايج (حقيقية، bge-m3 على Ollama 0.32.15)

```
BM25        مفيش ولا نتيجة
Embeddings  [('Error TS-999', 0.44), ('سياسة الاسترداد', 0.39), ('Error TS-404', 0.36)]
Hybrid      ['Error TS-999', 'سياسة الاسترداد', 'Error TS-404']
```

```
right section in the top 1:
  BM25        5/12
  Embeddings  10/12
  Hybrid      8/12
right section in the top 3:
  BM25        6/12
  Embeddings  11/12
  Hybrid      11/12
```

**المفاجأة:** الـ Hybrid خسر قدام الـ Embeddings في المركز الأول على الداتا دي.
مثال: «رقم خدمة العملاء كام؟» — الـ BM25 مسك كلمة «رقم» من «رقم الهاتف» في صفحة الباسورد، وشدّ الـ Hybrid معاه.
الدرس: مفيش best practice بتشتغل على كل داتا. قيس على داتا العميل نفسه، وبعدين قرّر.

الدرس الجاي: **Reranking** بـ Claude.
