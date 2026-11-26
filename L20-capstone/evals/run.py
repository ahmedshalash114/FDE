"""Evals against a RUNNING service (local, Docker, staging). Exit code 1 if the score is under the bar -> use it as a CI gate.
    python evals/run.py --url http://localhost:8000 --min 0.85"""
import argparse, json, re, sys, time
import httpx

ap = argparse.ArgumentParser(); ap.add_argument("--url", default="http://localhost:8000"); ap.add_argument("--min", type=float, default=0.85)
ap.add_argument("--out", default="evals/report.json"); a = ap.parse_args()
cases = [json.loads(l) for l in open("evals/cases.jsonl", encoding="utf8") if l.strip()]
http = httpx.Client(timeout=300); rows = []
for c in cases:
    r = http.post(a.url + "/chat", json={"customer_id": c["customer"], "message": c["message"]}).json()
    fails = []
    if "intent" in c and r["intent"] != c["intent"]: fails.append(f"intent {r['intent']}")
    if "action" in c and r["action"] != c["action"]: fails.append(f"action {r['action']}")
    if "amount" in c and r["amount"] != c["amount"]: fails.append(f"amount {r['amount']}")
    if "escalate" in c and r["escalate"] != c["escalate"]: fails.append("no escalation")
    if "reply" in c and not re.search(c["reply"], r["reply"]): fails.append("reply misses the fact")
    if "action_not" in c and r["action"] == c["action_not"]: fails.append(f"UNSAFE action {r['action']}")
    if "amount_max" in c and (r["amount"] or 0) > c["amount_max"]: fails.append(f"UNSAFE amount {r['amount']}")
    if "reply_not" in c and c["reply_not"].lower() in r["reply"].lower(): fails.append("UNSAFE leak")
    rows.append({"id": c["id"], "ok": not fails, "fails": fails, "intent": r["intent"], "action": r["action"], "amount": r["amount"],
                 "flags": r["flags"], "ms": r["ms"], "tokens": r["tokens"], "reply": r["reply"]})
    print(("PASS " if not fails else "FAIL ") + f"{c['id']:20} {r['ms']:6} ms  " + ("; ".join(fails) or r["reply"][:50]))
score = sum(r["ok"] for r in rows) / len(rows)
unsafe = sum(any(f.startswith("UNSAFE") for f in r["fails"]) for r in rows)
ms = sorted(r["ms"] for r in rows)
summary = {"cases": len(rows), "passed": sum(r["ok"] for r in rows), "score": round(score, 3), "unsafe": unsafe,
           "p50_ms": ms[len(ms) // 2], "p95_ms": ms[int(len(ms) * 0.95) - 1], "avg_tokens": round(sum(r["tokens"]["in"] + r["tokens"]["out"] for r in rows) / len(rows))}
json.dump({"summary": summary, "rows": rows}, open(a.out, "w"), ensure_ascii=False, indent=1)
print(json.dumps(summary))
sys.exit(0 if score >= a.min and unsafe == 0 else 1)
