"""L18 on Claude: the four levers for cost and latency.
  1) Don't think when the task doesn't need it   -> Haiku 5.5, effort "low" or thinking disabled, for classification
  2) Route: the cheap model first, the strong one only where it matters (Haiku 5.5 is 20x cheaper than Sonnet 5.5)
  3) Not urgent? Batch API = 50% off (results within 24h, usually much sooner)
  4) Stream: the user feels the FIRST token, not the last one
(+ prompt caching from L11 for long, repeated prefixes — this system prompt is too short to be cached.)
Needs ANTHROPIC_API_KEY.   python claude_cost.py
Prices: $ per million tokens, prompts up to 100K tokens — check https://platform.claude.com/docs/en/about-claude/pricing
"""
import json, time
import anthropic
from latency import MSGS, INTENTS, SYS, REPLY_SYS

client = anthropic.Anthropic()
SMALL, BIG = "claude-haiku-5-5", "claude-sonnet-5-5"
PRICE = {SMALL: (0.10, 0.50), BIG: (2.00, 10.00)}
SCHEMA = {"type": "object", "properties": {"intent": {"type": "string", "enum": INTENTS}}, "required": ["intent"], "additionalProperties": False}

def cost(model, usage, batch=False):
    pin, pout = PRICE[model]
    usd = (usage.input_tokens * pin + usage.output_tokens * pout) / 1e6
    return usd * (0.5 if batch else 1)

def classify(msg, thinking=False):
    """Classification = no thinking needed. Haiku 5.5 thinks adaptively by default (effort medium);
    for a one-word answer turn it off (allowed at effort high or below) or use effort 'low'."""
    kw = {} if thinking else {"thinking": {"type": "disabled"}}
    t0 = time.time()
    r = client.messages.create(model=SMALL, max_tokens=50 if not thinking else 2000, system=SYS, messages=[{"role": "user", "content": msg}],
                               output_config={"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}}, **kw)
    text = "".join(b.text for b in r.content if b.type == "text")
    return json.loads(text)["intent"], r.usage, round((time.time() - t0) * 1000)

def reply(msg, intent):
    """Route: only complaints go to the strong model; everything else stays on Haiku. Streamed."""
    model = BIG if intent == "complaint" else SMALL
    t0, first, text = time.time(), None, ""
    with client.messages.stream(model=model, max_tokens=300, system=REPLY_SYS, messages=[{"role": "user", "content": msg}]) as s:
        for chunk in s.text_stream:
            if first is None and chunk: first = time.time() - t0
            text += chunk
        usage = s.get_final_message().usage
    return model, text, usage, round(first * 1000), round((time.time() - t0) * 1000)

def nightly_batch():
    """Not urgent (e.g. tag yesterday's tickets for the weekly report)? Send them as one batch: half price."""
    b = client.messages.batches.create(requests=[
        {"custom_id": f"msg-{i}", "params": {"model": SMALL, "max_tokens": 50, "system": SYS, "thinking": {"type": "disabled"},
                                             "output_config": {"format": {"type": "json_schema", "schema": SCHEMA}},
                                             "messages": [{"role": "user", "content": m}]}}
        for i, (m, _) in enumerate(MSGS)])
    print("batch", b.id, b.processing_status, "— poll client.messages.batches.retrieve(id), then .results(id)")
    return b.id

def per_month(out_tokens_per_msg, in_tokens_per_msg=120, msgs_per_day=10_000, model=SMALL, batch=False):
    pin, pout = PRICE[model]; n = msgs_per_day * 30
    return round(n * (in_tokens_per_msg * pin + out_tokens_per_msg * pout) / 1e6 * (0.5 if batch else 1), 2)

if __name__ == "__main__":
    total, ok = 0.0, 0
    for msg, gold in MSGS:
        intent, u, ms = classify(msg)
        ok += intent == gold; total += cost(SMALL, u)
        model, text, u2, ttft, all_ms = reply(msg, intent)
        total += cost(model, u2)
        print(f"{intent:9} {'ok ' if intent == gold else 'XX '} {ms:5} ms | {model:17} first token {ttft} ms / all {all_ms} ms | {text[:50]}")
    print(f"\n{ok}/20 correct, ${total:.4f} for 20 messages (classify + reply)")
    # what the same token counts we measured on qwen (results.json) would cost per month at 10,000 messages/day:
    for name, out_tok in [("think", 1184.7), ("plain", 2.2), ("schema", 10.5)]:
        print(f"{name:7} Haiku 5.5 ${per_month(out_tok):>9}  | Sonnet 5.5 ${per_month(out_tok, model=BIG):>9} | Haiku batch ${per_month(out_tok, batch=True):>9}")
