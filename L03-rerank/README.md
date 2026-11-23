# L03 · Reranking + Contextual Retrieval — والنتيجة عكس المتوقع

الكود بتاع الدرس التالت من سلسلة **FDE Academy**، على عناوين Anthropic Academy:
*Reranking results → Contextual retrieval* (آخر قسم الـ RAG في كورس *Building with the Claude API*).

- `rerank.py`: الـ Hybrid (من L02) بيجيب 6 مرشحين، والـ LLM بيقرأهم ويرتّبهم من جديد.
  الرد بيبدأ بـ **prefill** (`{"ids": [`) وبيقف عند `]` بـ **stop_sequences**، فبيرجع أرقام بس.
  وفيه **guard**: أي رقم مش من المرشحين اللي بعتناهم بيترمي.
- `contextual.py`: **Contextual Retrieval** بنفس الـ prompt بتاع Anthropic: الموديل بيكتب سطر context لكل chunk قبل الـ indexing.
- `evals.py`: نفس الـ 12 سؤال بالمصري من L02، على 4 تركيبات.
- `rag2.py` و `docs.md`: من L02 زي ما هم.

## الموديل

الكود بيستخدم **Anthropic SDK** نفسه، بس شغّال على موديل local ببلاش: `qwen3.5:4b` على **Ollama**
(Ollama بيدعم Claude Messages API). عايز تشغّله على Claude؟ غيّر سطرين في `rerank.py`:

```python
client = Anthropic()            # بياخد ANTHROPIC_API_KEY من الـ environment
MODEL = "claude-haiku-4-5"
```

## شغّله

```bash
ollama pull bge-m3
ollama pull qwen3.5:4b
pip install -r requirements.txt
python rerank.py "رقم خدمة العملاء كام؟"
python contextual.py
python evals.py
```

## النتايج (حقيقية، qwen3.5:4b + bge-m3 على Ollama، اتشغّلت مرة واحدة)

```
Hybrid   ['الحساب وكلمة المرور', 'الدعم الفني', 'طرق الدفع']
Reranked ['الدعم الفني', 'طرق الدفع', 'الشحن والتوصيل']
```

```
Hybrid               top1  8/12   top3 11/12
Hybrid + Rerank      top1  8/12   top3 10/12
Contextual           top1  7/12   top3  9/12
Contextual + Rerank  top1  6/12   top3  8/12
```

- الـ reranker صلّح سؤالين (منهم فخ L02: «رقم خدمة العملاء كام؟») وبوّظ سؤالين.
- في «ينفع أقسط؟» رجّع id رقم 2 وهو مكانش من المرشحين أصلًا، عشان كده الـ guard.
- الـ context اللي كتبه الموديل الصغير لكذا فقرة كان فهرس المستند كله
  («سياسة الاسترداد، الاستبدال، الشحن والتوصيل، ...»)، فالفقرات بقت شبه بعض والبحث اتلخبط.

Anthropic قاست Contextual Retrieval بـ Claude على داتا كبيرة: الفشل قل 49% (و67% مع الـ reranking).
هنا بموديل 4B على 12 فقرة: أوحش. الـ techniques فرضيات؛ الـ evals على داتا العميل هي اللي بتقرر.

المرجع: [Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval) ·
[Building with the Claude API](https://anthropic.skilljar.com/claude-with-the-anthropic-api)

الدرس الجاي: **L04 · أول API call مع Claude من الصفر**.
