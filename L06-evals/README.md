# L06 · Prompt Evals — الـ unit test بتاع الـ prompts

الكود بتاع الدرس السادس من سلسلة **FDE Academy**، على قسم *Prompt evaluation* في كورس Anthropic Academy
*Building with the Claude API*: A typical eval workflow → Generating test datasets → Running the eval → Model based grading → Code based grading.

في L05 «منى» وعدت العميل إن فلوسه هترجع «غدًا». هنا بنقيس ده بيحصل كام مرة، ونصلّحه، ونقيس تاني.

- `mona.py`: الـ policy و system prompt «منى» بنسختين: V1 (نفس L05) و V2 (V1 + سطر واحد: *Never promise a day or a time. Refunds take 5 to 7 working days.*).
- `dataset.py`: الموديل بيكتب 8 رسايل عملاء (prefill ` ```json ` + stop sequence)، وبنزوّد 4 بإيدينا عن الاسترداد → `dataset.json` (12 حالة).
- `graders.py`:
  - `code_grade`: قصير (جملتين، ≤ 220 حرف)، من غير markdown، ومن غير ما يوعد بيوم (غدًا / بكرة / النهارده).
  - `model_grade`: الموديل بيقرا الرد قصاد الـ policy ويرجّع JSON فيه `reason` و `score` من 1 لـ 10.
- `run_eval.py`: بيشغّل V1 و V2 على الـ 12 حالة ويطبع النتيجة.
- `client.py`: نفس L04.

## شغّله

```bash
ollama pull qwen3.5:4b
pip install -r requirements.txt
python dataset.py      # optional: dataset.json موجود جاهز
python run_eval.py
```

عايز Claude؟ في `client.py`: `client = Anthropic()` و `MODEL = "claude-haiku-4-5"`.

## النتايج الحقيقية (qwen3.5:4b على Ollama، اتشغّلت مرة واحدة)

```
== V1: code checks passed 11/12 · model score avg 6.1/10
== V2: code checks passed 12/12 · model score avg 9.2/10
```

| | V1 | V2 |
|---|---|---|
| model scores | 2 6 6 3 2 2 10 8 8 10 8 8.5 | 10 9 9 8 10 10 10 8 8 10 9 9 |

- **راجع الداتا:** نص الرسايل اللي الموديل كتبها فصحى، وواحدة مش مفهومة خالص («أرسلوني عداداً للمنتج المالك كذا»). عشان كده زوّدنا 4 بإيدينا.
- **أوحش رد في V1:** «كم وقت لازم ليصللي من الآن؟» → «آسف يا بطل، لكنك كتقدر تسألني فقط في حالات البائع الخائن أو ما فيه قانون.» درجة 2.
- **راجع الـ grader كمان:** طلبنا رقم صحيح من 1 لـ 10، ورجّع `8.5`. لو كودك بيعمل `:2d` أو `int(...)` هيقع. اعمل validation على الـ JSON اللي راجع.
- **حدود صريحة:** تشغيلة واحدة على 12 حالة. في الشغل الحقيقي: حالات أكتر، وتكرار كل حالة كذا مرة، ومقارنة المتوسطات.

الدرس الجاي: **L07 · Tool use** — منى تسأل الـ database بنفسها عن الأوردر.
