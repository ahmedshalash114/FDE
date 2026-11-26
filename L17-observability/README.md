# L17 · Observability — 200 OK doesn't mean right

Every model call becomes **one JSON line** (a trace): input, output, tokens, time, prompt version. On every line, **cheap checks in plain code** — no extra model calls:
`fusha` (reads like Modern Standard Arabic instead of Egyptian), `promise` (a time/date we never gave it), `too_long`, `slow` (> 3 s).

Same 20 customer messages (from L12), `qwen3.5:4b` on Ollama, one real run:

| | prompt v1 | prompt v2 (fixed after reading the v1 traces) |
|---|---|---|
| HTTP OK | 20 / 20 | 20 / 20 |
| replies in fusha | **13** | **0** |
| invented promises ("خلال اليوم", "خلال يومين") | **2** | **0** |
| slow (> 3 s) | 1 — the first call that ran: 3.4 s of it was loading the model (cold start) | 0 |
| clean on all checks | 6 | 20 |
| avg output tokens | 43 | 30 |

## The twist
v2 passes every check… but read the replies: *«هراجع جزماتك بالأخوية»*, *«عفا الله من كدا، بيقولني واحد إنهم بيديوك فحوص»*. Forcing the small model into dialect fixed the **shape** and broke the **meaning**. Checks only catch what they measure — someone still has to read a sample (or have a stronger model grade it, L06).

Honest notes:
- The word lists in `checks()` are rough, and I wrote them after reading the v1 traces (that's the loop: look → define a check → fix → measure again). They miss some fusha (e.g. words with a و prefix).
- The slow call wasn't the prompt's fault: v2 ran with the model already in memory. The fix for cold starts is `keep_alive`, not prompting.

## Files
- `obs.py` — `traced()` writes the JSONL, `checks()` runs on every trace, `dashboard()` aggregates. Prompts v1 and v2.
- `traces_v1.jsonl`, `traces_v2.jsonl`, `dashboard.json` — the run.
- `claude_obs.py` — the same trace line for Claude calls: `request_id`, input/output tokens, cache reads/writes, `stop_reason`, cost, time (not run in the video; needs `ANTHROPIC_API_KEY`).
- `messages.py` — the 20 messages.

```bash
pip install -r requirements.txt
ollama pull qwen3.5:4b
python obs.py
```
Next: **L18 · Cost & latency**.
