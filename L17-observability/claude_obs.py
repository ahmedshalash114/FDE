"""Tracing Claude calls: one JSON line per call with everything you need when something goes wrong later.
Keep the request id (support can find the call), tokens (cost), cache hits (L11), stop_reason (cut off?) and timing.
Ship the same lines to any log store (or an OpenTelemetry / LLM-observability tool) — the schema matters more than the tool.
Needs ANTHROPIC_API_KEY.   python claude_obs.py
"""
import json, time, uuid
import anthropic
from obs import checks, PROMPTS
from messages import MESSAGES

client = anthropic.Anthropic()
PRICE = {"claude-haiku-5-5": (0.10, 0.50)}   # $ per million input / output tokens (prompts up to 100K) — check the current price list

def traced(model, system, msg, version, user_id=None):
    t0 = time.time()
    r = client.messages.create(model=model, max_tokens=300, system=system, messages=[{"role": "user", "content": msg}])
    ms = round((time.time() - t0) * 1000)
    reply = "".join(b.text for b in r.content if b.type == "text")
    u = r.usage; pin, pout = PRICE[model]
    trace = {"trace_id": uuid.uuid4().hex[:12], "request_id": r._request_id, "ts": time.time(), "version": version, "user": user_id,
             "model": r.model, "input": msg, "output": reply, "stop_reason": r.stop_reason,
             "input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
             "cache_read": u.cache_read_input_tokens, "cache_write": u.cache_creation_input_tokens,
             "cost_usd": round((u.input_tokens * pin + u.output_tokens * pout) / 1e6, 6), "ms": ms}
    trace["checks"] = checks(reply, ms)
    with open("claude_traces.jsonl", "a") as f: f.write(json.dumps(trace, ensure_ascii=False) + "\n")
    return trace

if __name__ == "__main__":
    for m in MESSAGES[:5]:
        t = traced("claude-haiku-5-5", PROMPTS["v2"], m[0], "v2")
        print(t["ms"], "ms", t["output_tokens"], "tok", t["checks"], t["output"][:60])
