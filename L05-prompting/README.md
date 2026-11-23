# L05 · Prompt Engineering — بالأرقام

الكود بتاع الدرس الخامس من سلسلة **FDE Academy**، على قسم *Prompt engineering techniques* في كورس Anthropic Academy
*Building with the Claude API*: Being clear and direct → Being specific → Structure with XML tags → Providing examples.

- `prompts.py`: 4 نسخ من نفس الـ prompt (V1 غامضة، V2 واضحة، V3 محددة + XML tags، V4 + أمثلة).
- `eval.py`: نفس الـ 12 سؤال من L02، ولكل سؤال الـ label المتوقع. بيطبع الـ score لكل نسخة.
- `reply.py`: system prompt لموظفة خدمة عملاء اسمها «منى»: قواعد + policy + مثال، كلهم في XML tags.
- `client.py`: نفس L04.

## شغّله

```bash
ollama pull qwen3.5:4b
pip install -r requirements.txt
python eval.py
python reply.py
```

عايز Claude؟ في `client.py`: `client = Anthropic()` و `MODEL = "claude-haiku-4-5"`.

## النتايج الحقيقية (qwen3.5:4b على Ollama، اتشغّلت مرة واحدة)

```
V1 vague        0/12   e.g. 'هذه الرسالة تُصنف على أنها **رسالة عاطفي'
V2 clear       10/12   e.g. 'refund'
V3 + XML       12/12   e.g. 'refund'
V4 + examples  12/12   e.g. 'refund'
```

- V2 غلط في اتنين: «الموبايل بايظ من المصنع» → `account` (المتوقع `warranty`)، و«بيقولي TS-500» → `support` (المتوقع `error`).
  تعريف كل label في سطر (V3) صلّحهم.
- `reply.py`:
  ```
  فعل كده بس لازم منتجك جديد وبتوصل فيه 14 يوم.
  اشوف إيه رقم الأوردر اللي عندك لأرجعلك فلوسك غدا أو المدينين من أول.
  ```
  عامية، جملتين، وطلب رقم الأوردر… بس قال «غدًا» والـ policy بتقول 5 لـ 7 أيام عمل. ده اللي الـ evals بتمسكه.

الدرس الجاي: **L06 · Prompt Evals**.
