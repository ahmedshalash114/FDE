# L07 · Tool Use — منى تسأل الداتابيز بنفسها

الكود بتاع الدرس السابع من سلسلة **FDE Academy**، على قسم *Tool use with Claude* في كورس Anthropic Academy
*Building with the Claude API*: Introducing tool use → Tool functions → Tool schemas → Handling message blocks → Sending tool results → Multi-turn conversations with tools.

- `db.py`: بيعمل `orders.db` (SQLite) فيها 5 أوردرات (1042 … 1046). أوردر 1047 مش موجود عن قصد.
- `tools.py`: فنكشنين بايثون عاديين (`get_order`, `get_refund`) + الـ schemas بتاعتهم (`name`, `description`, `input_schema`).
- `mona.py`: system prompt «منى» (من L06) + `SYSTEM_TOOLS` = نفس الـ prompt + سطر واحد: *Before you answer anything about an order, call get_order.*
- `agent.py`: الـ loop: طول ما `stop_reason == "tool_use"` → شغّل كل `tool_use` block، ورجّع `tool_result` بنفس الـ `tool_use_id`، واسأل تاني.
- `eval_tools.py`: 6 أسئلة × 3 طرق (من غير tools / tools / tools + السطر)، والـ grader بالموديل من L06 بيقارن الرد بالداتابيز.
- `results.json`: نتايج التشغيلة الحقيقية.

## شغّله

```bash
ollama pull qwen3.5:4b
pip install -r requirements.txt
python db.py
python agent.py "لغيت أوردر 1046، الفلوس رجعت؟"
python eval_tools.py
```

عايز Claude؟ في `client.py`: `client = Anthropic()` و `MODEL = "claude-haiku-4-5"`.

## النتايج الحقيقية (qwen3.5:4b على Ollama، اتشغّلت مرة واحدة)

```
$ python agent.py "لغيت أوردر 1046، الفلوس رجعت؟"
  -> get_order({'order_id': 1046}) = {"order_id": 1046, "item": "شاشة 27 بوصة", "status": "cancelled", "eta": null}
  -> get_refund({'order_id': 1046}) = {"order_id": 1046, "refund": "refunded on 2026-11-21"}
Mona: نعم، الفلوس رجعت يوم 21 نوفمبر.
```
(الموديل طلب الـ tool-ين في رسالة واحدة.)

| | tool calls | ردود مطابقة للداتابيز |
|---|---|---|
| من غير tools | — | 0/6 |
| tools من غير السطر | 0/6 | 2/6 (بالتخمين، من غير ما يفتّش) |
| tools + السطر | 5/6 | 3/6 |

- **من غير tools:** «الرجوع مفيش عشان اللغات تطلب كويس، والفلوس ما رجعت بعد.» والداتابيز بتقول: refunded on 2026-11-21.
- **tools من غير السطر:** ولا tool call. وعن أوردر 1047 (مش موجود): «أنا هتفتشلك حالة الأوردر 1047 بس انتظر لحظة.» ومفتّشتش حاجة.
- **tools + السطر:** 1047 → «لا، الـ Order رقم 1047 مش موجود.» ✓ — بس 1043: الـ tool رجّع `eta: 2026-11-25` والرد قال «يوم الغد» (النهارده 23). قرا صح وكتب غلط.
- `tool_choice: {"type": "any"}` اتجاهل على Ollama في التجربة دي. ولما شغّلنا الـ thinking، الموديل نادى الـ tool من غير السطر الزيادة — ده موضوع L08.
- **حدود صريحة:** موديل 4B على اللابتوب، تشغيلة واحدة على 6 أسئلة. الـ grader نفسه بيغلط ساعات (راجع `reason` في `results.json`).

الدرس الجاي: **L08 · Extended thinking**.
