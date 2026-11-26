# L18 · Cost & latency — the cheapest token is the one you don't generate

One small task: **classify a customer message** (`status`, `refund`, `cancel`, `complaint`, `other`).
Same 20 messages (with gold labels), same model (`qwen3.5:4b` on Ollama), one real run, three ways to ask:

| | thinking ON | thinking OFF ("intent word only") | OFF + JSON schema (enum) |
|---|---|---|---|
| correct | 16 / 20 | **18 / 20** | 16 / 20 |
| output tokens / message (avg) | **1,185** | **2.2** | 10.5 |
| time / message (p50) | 19 s | **0.34 s** | 0.61 s |
| time / message (p95) | 122 s | 0.38 s | 0.68 s |
| whole run (20 messages) | **12 min** | **7 s** | 12 s |
| no answer at all | 3 | 0 | 0 |

- Thinking on a one-word task: ~540× more tokens, ~55× slower, and *less* accurate. Three messages thought for ~2 minutes until the 4,096-token context was full and never answered.
- The schema didn't help here: «شكرا الطلب وصل» and «جالي لون غلط» both came back `status`. A schema guarantees the **shape**, not the answer (and the `format` scaffolding costs ~8 tokens). Measure, don't assume.
- Streaming a full reply (5 messages): first token after **0.27–0.35 s**, the whole reply after **1.2–1.7 s**. Users feel the first token — stream.

## On Claude (`claude_cost.py`, not run in the video — needs `ANTHROPIC_API_KEY`)
1. **Don't think when the task doesn't need it.** Haiku 5.5 uses adaptive thinking by default (effort `medium`). For classification send `thinking={"type": "disabled"}` (allowed at effort `high` or below) or `output_config={"effort": "low"}`.
2. **Route:** Haiku 5.5 for routine messages, Sonnet 5.5 only for complaints. ($0.10 / $0.50 vs $2 / $10 per million input / output tokens, prompts up to 100K — check the [pricing page](https://platform.claude.com/docs/en/about-claude/pricing).)
3. **Batch** what isn't urgent: the Message Batches API is 50% off.
4. **Stream** replies.
5. Prompt caching (L11) only pays off for long, repeated prefixes — this system prompt is too short to cache.

Per month at 10,000 messages/day — an **estimate** using the output tokens we measured on qwen (Claude's own counts will differ) + ~120 input tokens per message:

| | Haiku 5.5 | Sonnet 5.5 | Haiku 5.5 + Batch |
|---|---|---|---|
| thinking (1,185 out tok) | $181 | **$3,626** | $91 |
| no thinking (2.2 out tok) | **$3.93** | $79 | **$1.97** |

## Files
- `latency.js` — the experiment as it was run (pasted in a browser tab on `http://localhost:11434`).
- `latency.py` — the same experiment in Python; `python latency.py` rewrites `results.json` and prints the table.
- `results.json` — the run: every classification (mode, gold, answer, output tokens, thinking chars, ms) + the 5 streamed replies.
- `claude_cost.py` — the four levers on Claude + the per-month calculator.

Honest notes: one run on one laptop; p95 of 20 messages is just the 19th value. The streamed replies themselves were still mostly fusha (that was L17's problem — speed doesn't fix quality).

```bash
pip install -r requirements.txt
ollama pull qwen3.5:4b
python latency.py
```
Next: **L19 · Fine-tuning vs RAG vs prompting**.
