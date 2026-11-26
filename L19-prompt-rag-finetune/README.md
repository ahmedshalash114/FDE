# L19 · Prompt vs RAG vs fine-tuning — which tool for which problem?

Same model (`qwen3.5:4b` on Ollama, thinking off), one real run (`results.json`).

## 1 · Knowledge: 12 questions about Mona Store's *own* policy
The policy is 12 short chunks (returns 14 days, Cairo shipping 45 EGP, free above 1,500, headphones warranty 6 months…). The model can't know any of it.

| | correct | wrong | "not sure" | prompt tokens / question |
|---|---|---|---|---|
| **prompt only** (persona, no facts) | 1 / 12 | **9** | 2 | 53 |
| **whole policy in the prompt** | **11 / 12** | 1 | 0 | 424 |
| **RAG** (top-3 chunks, character 3-gram TF-IDF) | **11 / 12** | 1 | 0 | **170** |

- Prompt only: 9 confident inventions — «7 أيام» for returns, «مجاني بالكامل لجميع المنتجات» for shipping, «ضمان لمدة عام» for headphones. The one "correct" (6-month installments) was a lucky guess.
- RAG = same score as stuffing the whole policy with **2.5× fewer tokens**.
- RAG's miss: «أقدر أرجّعها لحد إمتى؟» — the search returned the wrong 3 chunks (customer-service hours, cash on delivery, Cairo shipping), so the model said «أنا مو متأكدة» (graded *wrong* by the regex, which doesn't know «مو متأكدة» — honestly it's an "I'm not sure"). RAG is only as good as its search.
- Stuffing's miss: asked how long a refund takes, it answered without the "7 working days".

## 2 · A fact changes: Cairo shipping 45 → 60 EGP
Edit one line of the policy and ask again: whole-policy **60 ✓**, RAG **60 ✓**, prompt-only invented «25 … 40». Nothing to retrain. A fine-tuned model would need retraining for every price change.

## 3 · Behaviour: does adding examples fix the intent classifier? (L18's 20 messages)
| | correct | prompt tokens |
|---|---|---|
| instructions only | 17 / 20 | 75 |
| + 6 worked examples (written after seeing L18's mistakes, not copies of the test messages) | 17 / 20 | 157 |

Same score, different mistakes, twice the prompt. Examples aren't magic — measure. (Zero-shot here is 17 vs 18 in L18: different token budget and run-to-run variance on 20 messages.)

## The ladder
1. **Prompt + examples** — always start here.
2. **Facts? Give them to the model** — small: all of it in the prompt (cache it on Claude, L11); big: RAG (L01–L03).
3. **Fine-tune last** — only for *behaviour* prompting can't reach, with lots of labelled data, and evals (L06) that prove it.

On Claude: the only fine-tuning offered was Claude 3 Haiku on Amazon Bedrock ([announcement](https://www.anthropic.com/news/fine-tune-claude-3-haiku-ga)), and that model has reached end of life ([AWS model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-3-haiku.html): Sep 10, 2026 in most regions). Your tools are prompt, examples, context/RAG and evals.

## Files
- `choose.js` — the experiment as it was run (browser tab on `http://localhost:11434`); the 12 policy chunks, 12 questions + gold regexes, 6 examples.
- `choose.py` — the same in Python (reads the data from `choose.js`; part 3 reads the messages from `../L18-cost-latency/latency.js`).
- `results.json` — every answer, grade, prompt tokens, retrieved chunks, time.
- `claude_choose.py` — the three modes on Claude Haiku 5.5 (not run in the video; needs `ANTHROPIC_API_KEY`).

```bash
pip install -r requirements.txt
ollama pull qwen3.5:4b
python choose.py
```
Next: **L20 · Capstone — FastAPI + Docker + evals**.
