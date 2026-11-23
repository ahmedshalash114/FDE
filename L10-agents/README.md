# L10 · Agents & Workflows — الحلقة الأخيرة

الكود بتاع الدرس العاشر والأخير من سلسلة **FDE Academy**، على قسم *Agents and workflows* في كورس Anthropic Academy
*Building with the Claude API*: Agents and workflows → Chaining → Routing → Workflows vs agents.

- `agent.py`: الـ agent من L07: الموديل هو اللي بيقرر ينادي `get_order` / `get_refund` (loop لحد `end_turn`).
- `workflow.py`: الكود هو اللي بيقرر الخطوات:
  1. **route** — model call صغير يصنّف الرسالة: `refund` / `status` / `other`
  2. **look up** — الكود ينادي `get_order` (و `get_refund` لو refund) كل مرة
  3. **write** — الموديل يكتب الرد من الحقايق (`<facts>` في الـ system prompt)
  4. **check** — checks بالكود (من L06: short, no_md, no_date) + مع `strict=True`: `grounded` (أي رقم في الرد لازم يكون في الـ facts) و `on_topic` (سؤال الشحن ميتكلمش عن فلوس)
  5. **retry** — لو check فشل: يكتب تاني مرة واحدة ومعاه القواعد اللي اتكسرت
- `compare.py`: agent vs workflow vs workflow+checks على الست أسئلة، بالـ grader من L07 (`eval_l07.py`).
- `results.json`: كل الردود، الـ route، الـ facts، الـ drafts، والـ checks.

## شغّله

```bash
ollama pull qwen3.5:4b
pip install -r requirements.txt
python db.py
python workflow.py "طلبي رقم 1043 هيوصل إمتى؟"
python compare.py
```

عايز Claude؟ في `client.py`: `client = Anthropic()` و `MODEL = "claude-haiku-4-5"`.

## النتايج الحقيقية (qwen3.5:4b على Ollama، اتشغّلت مرة واحدة)

| | الـ grader | مراجعة بإيدي | model calls |
|---|---|---|---|
| agent (L07: tools + سطر) | 3/6 | 3/6 | 11 |
| workflow (route → look up → write) | 3/6 | 2/6 | 12 |
| workflow + checks + retry | 5/6 | 4/6 | 15 |

- **routing:** 6/6 صح (1042/1043/1044/1047 = status، 1045/1046 = refund).
- **ليه الـ workflow الأول جاب 3/6 بس؟** الـ facts دايمًا موجودة، بس الموديل بيزوّد من عنده:
  - 1043 (eta = 2026-11-25): «حالك، الشاحنت موجهة للتحديث وإستلامها بين ٢٥ و ٢٧ نوفمبر.»
  - 1042 (سؤال شحن): «... إعادة الدفع تكون خلال يومين إلى أسبوع عمل من وقت التسليم.»
- **الـ checks + retry:** 3 drafts فشلوا → الـ retry صلّح 2:
  ```
  $ python workflow.py "طلبي رقم 1043 هيوصل إمتى؟"
    route=status  facts={"order": {"order_id": 1043, "item": "شاحن 65 وات", "status": "shipped", "eta": "2026-11-25"}}
    first draft failed ['grounded']: 'حالك، الشاحنت موجهة للتحديث وإستلامها بين ٢٥ و ٢٧ نوفمبر.'
  Mona: النموذج يقول ستصل يوم ٢٥ نوفمبر.
  ```
  و1044 كتب تاني وغلط تاني: «أووردر 1044 موجود والمنتج غير مدمر. المبلغ يرجع لك في 5 إلى 7 أيام عمل.»
- **الوقت:** حوالي 21 ثانية للست أسئلة (workflow + checks) مقابل حوالي 24 ثانية (agent) على نفس اللابتوب.
- **حدود صريحة:** موديل 4B، تشغيلة واحدة، 6 أسئلة، و grader بيغلط (راجع `reason`).

**الدرس:** الطريق معروف؟ workflow، وخلّي الكود يجيب الداتا دايمًا. مش معروف؟ agent. وفي الحالتين: checks بالكود و eval دايمًا.

عشر حلقات: RAG · prompts · evals · tools · thinking · MCP · agents. شكرًا إنك كمّلت 🙌
