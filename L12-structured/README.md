# L12 · Structured Outputs — الشكل مضمون… والمعنى؟

الحلقة 12 في **FDE Academy** (الموسم التاني)، عن *Structured data* و*Prefilling* في كورس Anthropic Academy *Building with the Claude API*،
ومعاهم Structured outputs بتاعة Claude.

منى بتقرا رسالة العميل وبتطلّع منها JSON للسيستم: `order_id`، و`intent` (status / refund / cancel / complaint / other)، و`urgent`.

- `messages.py`: عشرين رسالة حقيقية بالمصري، ومع كل واحدة الإجابة الصح (gold).
- `schema.py`: الـ JSON schema، ومعاه validator صغير.
- `extract.py`: أربع طرق على نفس العشرين رسالة:
  1. **prompt**: «Reply with JSON only».
  2. **prefill**: الرد بيبدأ بـ `{` (الحيلة بتاعة L04).
  3. **schema**: constrained decoding، والموديل ميقدرش يكتب token برّه الـ schema (في Ollama اسمه `format`).
  4. **schema + rules**: نفس الـ schema، ومعاه تعريف واضح لكل خانة في الـ system prompt.
- `claude_structured.py`: على Claude: `output_config={"format": {"type": "json_schema", "schema": ...}}`،
  أو `client.messages.parse(output_format=PydanticModel)` → `parsed_output`، أو tools بـ `"strict": True`.
- `results.json`: كل الردود، والتقييم بتاع كل رسالة.

## شغّله

```bash
ollama pull qwen3.5:4b
pip install -r requirements.txt
python extract.py
```

## النتايج الحقيقية (qwen3.5:4b على Ollama، تشغيلة واحدة، 20 رسالة)

| الطريقة | JSON سليم | مطابق للـ schema | الـ 3 خانات صح |
|---|---|---|---|
| prompt بس | 20 | 20 | 9 |
| prefill `{` | 18 | 17 | 9 |
| schema (constrained) | 20 | 20 | 8 |
| **schema + قواعد** | **20** | **20** | **15** |

- **prefill:** ردّين اتكسروا (`{...}` و `{`)، وفي رد تالت المفتاح اتغيّر من `urgent` لـ `urgency`.
- **ليه الـ schema جاب 8 بس؟** الموديل قال `urgent: true` على 14 رسالة من 20، والإجابة الصح 5 بس.
  الـ schema بيضمن إن الخانة boolean، بس مبيقولش للموديل إمتى تبقى true.
- **القواعد** (يعني إيه refund، وإن الزعل لوحده مش استعجال، وإن ١٠٨٥ = 1085) جابت النتيجة من 8 لـ 15.
  عدد `urgent: true` نزل من 14 لـ 5، و4 منهم صح.
- الغلطات اللي فضلت: 1045 (فلوس مرتجع → اتصنّف status)، و1072 (شاشة مكسورة → مش urgent)، و«بتوصلوا أسوان؟» → اتصنّف status.

**الدرس:** الـ schema بيضمن الشكل، والقواعد بتضمن المعنى، والـ eval هو اللي بيقيس.
