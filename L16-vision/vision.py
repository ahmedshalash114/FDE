"""Run the L16 experiment: open Ollama's page in a headless browser, load invoices.js (draws the invoices on a canvas
and calls qwen3.5:4b for each one: text layer / clean scan / phone photo) and print the score.
    pip install playwright && playwright install chromium
    ollama pull qwen3.5:4b && python vision.py
The video's numbers come from one run of the same invoices.js in a browser on the same machine as Ollama."""
import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    page = p.chromium.launch().new_page()
    page.goto("http://localhost:11434")
    page.add_script_tag(path="invoices.js")
    res = page.evaluate("runAll()")
json.dump(res, open("results.json", "w"), ensure_ascii=False, indent=1)
for m in ("text", "clean", "photo"):
    rs = [r for r in res if r["mode"] == m]
    print(f"{m:6s} fields {sum(sum(r['ok'].values()) for r in rs)}/40   invoices fully right {sum(all(r['ok'].values()) for r in rs)}/10   "
          f"tokens/invoice {rs[0]['prompt_tokens']}   avg {sum(r['ms'] for r in rs) / len(rs) / 1000:.1f}s")
