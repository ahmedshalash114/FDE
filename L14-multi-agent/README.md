# L14 · Multi-agent — one agent vs a team

**The team:** an orchestrator splits the customer message into tasks (constrained JSON, the L12 schema idea) → each task goes to a worker that sees **only its own data** (orders / prices / returns) → a writer merges the answers into one reply.
**The single agent:** Mona with all the data in one system prompt.

10 customer messages, each asking 2–3 things (23 questions). Every correct answer contains a number we can check in code (tracking code, price, days). `qwen3.5:4b` on Ollama, one real run.

| Store | One agent | Team (orchestrator + 3 workers + writer) |
|---|---|---|
| Small — 30 orders, 30 products | **22 / 23** · 10 calls · 12.6K tokens · 32 s | **22 / 23** · 42 calls · 15.8K tokens · 104 s (86 s with workers in parallel) |
| Big — 150 orders, 150 products | **16 / 23** (order questions **0 / 7**) | **19 / 23** (order questions 6 / 7) · 42 calls |

## What happened in the big store
The single prompt was ~5,000 tokens; Ollama's context window silently kept only the **last 2,050** (`prompt_eval_count` = 2050 on every call). The model only ever saw orders 1171–1180 and answered *"order 1031 isn't in the list, it starts at 1171"*. No error, no warning.
Each worker's prompt (orders ≈ 3,190 tokens, prices ≈ 1,730, returns ≈ 190) fits, so the team still finds the orders.
You can also raise the context (`num_ctx`) — but every model has a limit, and long prompts cost every call.

**Rule:** start with one agent. Split into a team when the context overflows, the work is separable, or the parts need different tools/permissions — and count the calls.

## Files
- `store.py` — the store data (small + big), the 10 messages and their gold numbers.
- `agents.py` — single agent, orchestrator/workers/writer, code-based grading. `python agents.py` (small) · `python agents.py --big`.
- `claude_agents.py` — the same on Claude: plan via `output_config.format`, workers in parallel with `asyncio.gather`, Haiku for workers, Sonnet for the plan (not run in the video; needs `ANTHROPIC_API_KEY`).
- `results.json`, `results_big.json` — the run (replies trimmed).

```bash
pip install -r requirements.txt
ollama pull qwen3.5:4b
python agents.py && python agents.py --big
```
Next: **L15 · Guardrails** — someone will try to trick Mona.
