"""L18 · Cost & latency on a local model (qwen3.5:4b via Ollama).
Same 20 messages, same model, three ways to ask "what does the customer want?":
  think  : thinking ON, free answer
  plain  : thinking OFF, "reply with the intent word only"
  schema : thinking OFF + JSON schema with an enum + tiny token budget
Then streaming: time to first token vs time to the whole reply.
    ollama pull qwen3.5:4b      # once
    python latency.py           # writes results.json and prints the table
(latency.js is the same experiment for a browser tab on http://localhost:11434 — that's how results.json was recorded.)
"""
import json, re, time, statistics as st
import httpx

URL = "http://localhost:11434/api/chat"
MODEL = "qwen3.5:4b"
MSGS = json.loads(re.search(r"const MSGS = (\[\[.*?\]\]);", open("latency.js", encoding="utf8").read()).group(1))
INTENTS = ["status", "refund", "cancel", "complaint", "other"]
SYS = ("Classify the customer message into one intent: status (where is my order), "
       "refund (money back, return or exchange an item), cancel, complaint, other.")
MODES = {
    "think":  dict(think=True,  system=SYS + " Reply with the intent word only.", opts={}),
    "plain":  dict(think=False, system=SYS + " Reply with the intent word only.", opts={"num_predict": 200}),
    "schema": dict(think=False, system=SYS, opts={"num_predict": 20},
                   format={"type": "object", "properties": {"intent": {"type": "string", "enum": INTENTS}}, "required": ["intent"]}),
}
REPLY_SYS = "You are Mona, the support agent of Mona Store (Egypt). Answer in Egyptian Arabic, at most two short sentences. Never promise a time or an amount."
http = httpx.Client(timeout=300)

def classify(msg, gold, mode):
    m, t0 = MODES[mode], time.time()
    body = {"model": MODEL, "stream": False, "think": m["think"], "options": m["opts"],
            "messages": [{"role": "system", "content": m["system"]}, {"role": "user", "content": msg}]}
    if "format" in m: body["format"] = m["format"]
    r = http.post(URL, json=body).json()
    text = (r["message"].get("content") or "").lower()
    try: got = json.loads(text)["intent"]
    except Exception: got = next((i for i in INTENTS if i in text), text.strip()[:20])
    return {"mode": mode, "msg": msg, "gold": gold, "got": got, "ok": got == gold, "out_tokens": r.get("eval_count"),
            "thinking_chars": len(r["message"].get("thinking") or ""), "ms": round((time.time() - t0) * 1000),
            "load_ms": round(r.get("load_duration", 0) / 1e6)}

def streamed(msg):   # what the user FEELS is the first word, not the last one
    t0, first, text = time.time(), None, ""
    body = {"model": MODEL, "stream": True, "think": False, "options": {"num_predict": 200},
            "messages": [{"role": "system", "content": REPLY_SYS}, {"role": "user", "content": msg}]}
    with http.stream("POST", URL, json=body) as r:
        for line in r.iter_lines():
            if not line.strip(): continue
            c = json.loads(line).get("message", {}).get("content")
            if c:
                if first is None: first = time.time() - t0
                text += c
    return {"msg": msg, "ttft_ms": round(first * 1000), "total_ms": round((time.time() - t0) * 1000), "reply": text}

def table(res):
    for mode in MODES:
        rows = [r for r in res["classify"] if r["mode"] == mode]; ms = sorted(r["ms"] for r in rows)
        print(f"{mode:7} {sum(r['ok'] for r in rows):2}/20 correct | {st.mean(r['out_tokens'] for r in rows):7.1f} out tok/msg"
              f" | p50 {st.median(ms)/1000:6.2f}s  p95 {ms[int(.95*len(ms))-1]/1000:6.2f}s | no answer: {sum(r['got'] == '' for r in rows)}")
    for s in res["stream"]: print(f"stream: first token {s['ttft_ms']} ms, whole reply {s['total_ms']} ms")

if __name__ == "__main__":
    classify(*MSGS[0], "plain")   # warm-up: load the model once (cold start was L17's story)
    res = {"classify": [classify(m, g, mode) for mode in MODES for m, g in MSGS], "stream": [streamed(m) for m, _ in MSGS[:5]]}
    json.dump(res, open("results.json", "w"), ensure_ascii=False, indent=1)
    table(res)
