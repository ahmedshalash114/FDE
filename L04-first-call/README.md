# L04 · أول API call مع Claude — من الصفر

الكود بتاع الدرس الرابع من سلسلة **FDE Academy**، على أول قسم في كورس Anthropic Academy *Building with the Claude API*:
*Making a request → Multi-turn conversations → System prompts → Response streaming → Structured data*.

- `client.py`: الـ client و `chat()`: كل request فيه `model` و `max_tokens` و `messages`.
- `memory.py`: الـ API مالوش ذاكرة. نفس السؤال من غير تاريخ ومع التاريخ.
- `system.py`: نفس رسالة العميل بـ system prompt عام وبـ system prompt بتاعنا.
- `stream.py`: الرد بيوصل حتة حتة (`client.messages.stream`).
- `extract.py`: JSON نضيف بالـ **prefill** (`` ```json ``) و **stop_sequences**، وبعدين `json.loads`.

## الموديل

**Anthropic SDK** نفسه، شغّال على `qwen3.5:4b` على **Ollama** ببلاش (Ollama بيدعم Claude Messages API).
عايز Claude؟ في `client.py` غيّر سطرين:

```python
client = Anthropic()            # بياخد ANTHROPIC_API_KEY من الـ environment
MODEL = "claude-haiku-4-5"
```

## شغّله

```bash
ollama pull qwen3.5:4b
pip install -r requirements.txt
python memory.py
python system.py
python stream.py
python extract.py
```

## النتايج الحقيقية (qwen3.5:4b، اتشغّلت مرة واحدة)

`memory.py`
```
1: أهلاً بك يا أحمد! يسعدني معرفتك. 👋 ...
2: أسمي **المساعد الذكي**، ولا أملك شخصية أو اسمًا خاصًا لأنني نموذج ذكاء اصطناعي. ...
3: اسمك **أحمد**، كما ذكرته في رسالتك الأولى! 🎉 ...
```
(input tokens: 28 من غير تاريخ، 84 مع التاريخ)

`system.py`
- generic: محاضرة عن النصب ونصيحة بالنيابة العامة، 300 token، `stop_reason: "max_tokens"` (اتقطع).
- ours: جملتين وطلب رقم الأوردر، 70 token.

`extract.py`
```
{'intent': 'complaint', 'order_id': '1042', 'angry': True}
<class 'bool'> 1042
```

ملحوظة: الـ Anthropic Python SDK الحالي (2.x) مفيهوش `temperature` في `messages.create`.

الدرس الجاي: **L05 · Prompt Engineering**.
