"""One function the rest of the app calls. Ollama by default; set LLM=claude (+ ANTHROPIC_API_KEY) for Claude Haiku 5.5."""
import os, time
import httpx

LLM = os.getenv("LLM", "ollama")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = os.getenv("MODEL", "qwen3.5:4b" if LLM == "ollama" else "claude-haiku-5-5")
_http = httpx.Client(timeout=120)

def chat(system: str, user: str, max_tokens: int = 150) -> dict:
    t0 = time.time()
    if LLM == "claude":
        import anthropic
        r = anthropic.Anthropic().messages.create(model=MODEL, max_tokens=max_tokens, system=system, thinking={"type": "disabled"},
                                                  messages=[{"role": "user", "content": user}])
        text = "".join(b.text for b in r.content if b.type == "text")
        return {"text": text, "in": r.usage.input_tokens, "out": r.usage.output_tokens, "ms": round((time.time() - t0) * 1000)}
    r = _http.post(OLLAMA_URL + "/api/chat", json={"model": MODEL, "stream": False, "think": False, "options": {"num_predict": max_tokens},
                   "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}).json()
    return {"text": r["message"].get("content") or "", "in": r.get("prompt_eval_count"), "out": r.get("eval_count"),
            "ms": round((time.time() - t0) * 1000)}
