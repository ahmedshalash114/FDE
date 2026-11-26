# L16 · Vision + PDFs — when not to trust the model's eyes

10 supplier invoices in Arabic (3 of them written with Arabic-Indic digits ٠-٩). From each one the model extracts 4 fields — `invoice_no`, `date`, `total`, `items` — so 40 fields. Same model (`qwen3.5:4b`, vision-capable) on Ollama, same schema, 3 ways in:

| Input | Fields right | Invoices fully right | Arabic-digit invoices (12 fields) | Prompt tokens / invoice | Avg time |
|---|---|---|---|---|---|
| **Text layer** (what a digital PDF gives you) | **39 / 40** | 9 / 10 | 12 / 12 | 213 | 2.7 s |
| **Clean scan** (PNG, 800 px) | **35 / 40** | 7 / 10 | 7 / 12 | 831 | 5.3 s |
| **Phone photo** (480 px, tilted, shadow, JPEG) | **25 / 40** | 2 / 10 | 3 / 12 | 356 | 3.3 s |

What went wrong in the images:
- Arabic digits: `١٩,٦١٩.٤٠` became `196194` (decimal point lost → ×10) on the scan and `1,995,831` on the photo.
- On the photo, `0` was read as `8` in invoice numbers (`INV-2026-0602` → `INV-2026-0682`), 5 of 10 times.
- The small photo used *fewer* tokens than the clean scan — and made more mistakes.

**Rules:** have the PDF? send its text. Only an image? higher resolution costs more tokens but reads better. And check what you can in code: `subtotal + VAT == total` (see `claude_vision.py`).

## Files
- `invoices.js` — draws the 10 invoices on a canvas (text layer / clean scan / phone photo), calls Ollama's `/api/chat` with a JSON schema, scores each field. This is exactly what ran for the video (in a browser tab on the Ollama machine).
- `vision.py` — runs `invoices.js` headless with Playwright and prints the table.
- `claude_vision.py` — on Claude: `image` blocks for photos/scans, `document` blocks for PDFs (Claude reads the text and sees each page), structured output, and an arithmetic check. Not run in the video; needs `ANTHROPIC_API_KEY`.
- `results.json` — every extraction vs the gold values.

```bash
pip install -r requirements.txt && playwright install chromium
ollama pull qwen3.5:4b
python vision.py
```
Next: **L17 · Observability** — Mona makes mistakes and you can't see them.
