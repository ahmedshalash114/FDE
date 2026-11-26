# L13 · Memory — Mona remembers the customer

The model remembers nothing. Every request starts from a blank page; even a "multi-turn" chat (L04) only works because *we* send the whole conversation again.

**The test:** 5 customers talked to Mona yesterday (an order number, a city, "WhatsApp only", "I paid by Visa", "I'm at work until 5"). Today each one comes back in a **new** conversation with a follow-up question. Did Mona use what they said?

| Mode | What goes into today's request | Remembered | Avg input tokens |
|---|---|---|---|
| `none` | today's question only | **0 / 5** | 68 |
| `history` | yesterday's whole conversation + today | **2 / 5** | 188 (and it grows every day) |
| `memory_v1` | a JSON memory extracted from the **whole** chat | **2 / 5** | 145 |
| `memory` | a memory extracted from the **customer's words only**, shown as readable lines | **3 / 5** | 136 |

One real run, `qwen3.5:4b` on Ollama, numbers in [`results.json`](results.json).

## What went wrong in v1 — memory can lie
Yesterday Mona told Sara *"your money will arrive within 24 working hours"* — Mona made that up. Memory v1 read the whole chat and saved it as a fact. The next day Mona told Sara *"yes, the money was refunded"*.
**Rule:** build memory from what the customer said, never from the model's own replies.

## Honest notes
- The fixed version is not perfect: Mariam's memory correctly says "at work until 5", but the small model ignored it in its answer.
- The 4B extractor also put junk in some fields (Sara's "city" became «الفلوس»). A bigger model, or a schema with stricter descriptions (L12), fixes most of this.
- "Remembered" = the reply contains the fact (order id / city / WhatsApp / Visa / 5) and does not ask for it again (`remembered()` in `memory.py`).

## Files
- `memory.py` — the 4 modes, the extractor (constrained JSON via Ollama `format`, the L12 schema idea), `render()` to readable lines, save/load per customer in `memories/`.
- `customers.py` — the 5 customers, yesterday + today, and the words that prove Mona remembered.
- `claude_memory.py` — the same idea on Claude with the built-in **memory tool** (`memory_20250818`): Claude decides what to save, your code stores the files (one folder per customer, path-checked), plus **context editing** (`clear_tool_uses_20250919`) for long agent runs. Needs `ANTHROPIC_API_KEY`; not run in the video.
- `memories/<name>.json` is created when you run `memory.py` (the saved memory per customer; the run's copies are inside `results.json`).

```bash
pip install -r requirements.txt
ollama pull qwen3.5:4b
python memory.py          # local run
python claude_memory.py   # on Claude
```

Next: **L14 · Multi-agent** — Mona is not alone.
