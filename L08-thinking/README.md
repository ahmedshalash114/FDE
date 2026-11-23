# L08 · Extended Thinking — فكّري الأول

الكود بتاع الدرس التامن من سلسلة **FDE Academy**، على قسم *Features of Claude → Extended thinking* في كورس Anthropic Academy *Building with the Claude API*.

نفس منى ونفس الـ tools ونفس الست أسئلة من **L07**، ونفس الـ system prompt **من غير** السطر الزيادة («call get_order…»). الفرق الوحيد:

```python
thinking={"type": "enabled", "budget_tokens": 2000}   # و max_tokens=4000 (لازم أكبر من الـ budget)
```

- `agent.py`: الـ loop من L07 + باراميتر `thinking`. الـ `msg.content` (ومعاه الـ thinking block) بيترجع زي ما هو مع الـ `tool_result`.
- `think_eval.py`: thinking off مقابل thinking on، والـ grader من L07 (`eval_l07.py`) + code check: لو الرد فاضي = fail.
- `results.json`: الردود، الـ tool calls، وأول 400 حرف من الـ thinking لكل سؤال (وطوله الكامل).

## شغّله

```bash
ollama pull qwen3.5:4b
pip install -r requirements.txt
python db.py
python think_eval.py
```

عايز Claude؟ في `client.py`: `client = Anthropic()` و `MODEL = "claude-haiku-4-5"`.

## النتايج الحقيقية (qwen3.5:4b على Ollama، اتشغّلت مرة واحدة)

| | tool calls | الـ grader | مراجعة بإيدي | الوقت | output tokens |
|---|---|---|---|---|---|
| thinking off | 0/6 | 2/6 | 2/6 (تخمين) | 18 s | 247 |
| thinking on | 5/6 | 5/6 | 4/6 | 158 s | 4,895 |

- **التفكير الحقيقي (1042):** *"The user is asking about the status and delivery date of order #1042. I need to use the get_order function to look up this order information."* → `tool_use: get_order(1042)`.
- **1045 و 1046:** نادت `get_order` و `get_refund` مع بعض.
- **الـ grader غلط:** 1046 → «يا هلا، الفلوس رجعت من يوم 21 نوفمبر بتاع الشهر اللي فات.» — الـ grader قال pass، والحقيقة إنها رجعت من يومين (النهارده 23).
- **1047 (مش موجود):** 103 ثانية، 3,558 token تفكير (12,552 حرف)، وآخر سطر: `Final Plan:` → `stop_reason: "max_tokens"` ومفيش رد خالص. وجوّه التفكير: *"I will assume the tool call was done internally and reply."*
- `budget_tokens: 2000` اتجاهل على Ollama. على Claude: `budget_tokens` لازم ≥ 1024 وأقل من `max_tokens`.
- **Prompt caching و Citations** في نفس القسم من الكورس، بس دول على Claude ومقستهمش على اللابتوب — فمفيش أرقام.
- **حدود صريحة:** موديل 4B، تشغيلة واحدة، 6 أسئلة.

الدرس الجاي: **L09 · MCP** — نحوّل الـ tools دي لـ server يستخدمه أي تطبيق.
