# L11 · Prompt Caching — الموسم التاني

أول درس في الموسم التاني من **FDE Academy**، على *Prompt caching* في قسم *Features of Claude* بكورس Anthropic Academy
*Building with the Claude API*.

منى عندها handbook حوالي ألفين token (شحن، مرتجعات، ضمان، FAQ). من غير caching، الموديل بيقرا الـ handbook كله من الأول مع كل سؤال.
الـ cache بيحتفظ بالجزء الأول من الـ prompt (الـ prefix)، والأسئلة اللي بعده بتكمّل من عنده.

- `handbook.py`: الـ handbook، وده الجزء الثابت اللي يستاهل يتعمله cache.
- `cache_demo.py`: نفس الخمس أسئلة بطريقتين:
  - **غلط:** اسم العميل والتاريخ في **أول** الـ system prompt ← الـ prefix بيتغير مع كل عميل، فمفيش حاجة بتتعاد.
  - **صح:** الـ handbook الأول، والاسم والتاريخ في **الآخر**.
- `claude_cache.py`: نفس الفكرة على Claude: `cache_control` على block الـ handbook، وبعدها بتقرا `usage.cache_creation_input_tokens` و`usage.cache_read_input_tokens`.
- `cost.py`: حسبة التكلفة على Claude Haiku 4.5.
- `results.json`: التشغيلة الحقيقية: الوقت والـ tokens والرد لكل نداء.

## شغّله

```bash
ollama pull qwen3.5:4b
pip install -r requirements.txt
python cache_demo.py
python cost.py
```

عايز Claude؟ في `client.py`: `client = Anthropic()` و `MODEL = "claude-haiku-4-5"`، أو شغّل `claude_cache.py` على طول.

## النتايج الحقيقية (qwen3.5:4b على Ollama 0.32.15، MacBook 16 GB، الموديل warm، تشغيلة واحدة)

ثواني لكل نداء (حوالي 2,060 input token):

| | 1 | 2 | 3 | 4 | 5 | المجموع |
|---|---|---|---|---|---|---|
| غلط: المتغير في الأول | 6.6 | 6.0 | 6.1 | 7.2 | 5.9 | **31.8s** |
| صح: الثابت في الأول | 6.3 | 2.1 | 2.4 | 3.3 | 2.1 | **16.3s** |

- أول نداء في الطريقة الصح بطيء لأن مفيش حاجة في الـ cache لسه. اللي بعده بيعيد استخدام الـ prefix.
- Ollama بيعيد استخدام الـ prefix لوحده (KV cache)، بس مبيرجعش عدادات الـ cache في الـ `usage`. Claude بيرجّعهم.
- تجربة صغيرة على نفس الجهاز: لما اتغير حرف في **أول** الـ prompt، النداء أخد 6.6 ثانية. ولما الحرف اتغير في **الآخر**، أخد 1.6 ثانية.

## Claude (أسعار نوفمبر 2026، Haiku 4.5، لكل مليون token)

| input | cache write (5 دقايق) | cache read |
|---|---|---|
| $1.00 | $1.25 (1.25×) | $0.10 (0.1×) |

- `cost.py`: handbook من 10,000 token و1,000 سؤال في اليوم: **$10.00 ← $1.14 في اليوم (89% أقل على الـ prefix)**.
  الحسبة فارضة 12 كتابة و988 قراية، والـ cache دافي طول اليوم.
- **خلي بالك:** Haiku 4.5 مبيعملش cache لأي prompt أقل من **4,096 token**، ومبيطلعش error.
  يعني الـ handbook بتاعنا (حوالي 2,000 token) مش هيتعمله cache على Haiku 4.5.
  اعرف من الـ usage: لو `cache_creation_input_tokens` و`cache_read_input_tokens` الاتنين صفر، يبقى مفيش cache.
- الـ cache بيعيش 5 دقايق، وبيتجدد ببلاش مع كل قراية. ولو عايزه يعيش ساعة: `{"type": "ephemeral", "ttl": "1h"}`، والكتابة بـ 2×.
- ترتيب الـ cache: `tools` ← `system` ← `messages`. أي تغيير في مستوى بيبوّظ المستوى ده واللي بعده.
- Automatic caching: `cache_control={"type": "ephemeral"}` على مستوى الـ request، والـ API بيحط الـ breakpoint لوحده.

**الدرس:** الثابت فوق، والمتغير تحت. وبعدها بص على الـ usage.
