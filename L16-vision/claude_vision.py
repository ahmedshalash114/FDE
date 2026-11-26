"""Invoices on Claude: an image block for photos/scans, a document block for PDFs
(Claude reads the PDF's text AND looks at each page as an image), and structured output for the fields.
Needs ANTHROPIC_API_KEY.   python claude_vision.py invoice.pdf  |  python claude_vision.py photo.jpg
"""
import base64, json, sys
import anthropic

client = anthropic.Anthropic()
SCHEMA = {"type": "object", "properties": {"invoice_no": {"type": "string"}, "date": {"type": "string"},
          "total": {"type": "number"}, "subtotal": {"type": "number"}, "vat": {"type": "number"}, "items": {"type": "integer"}},
          "required": ["invoice_no", "date", "total", "subtotal", "vat", "items"], "additionalProperties": False}
ASK = ("Extract from this supplier invoice: invoice_no, date (YYYY-MM-DD, western digits), subtotal, vat, total "
       "(numbers, western digits; Arabic-Indic digits ٠-٩ must be converted) and items (number of product lines).")

def block(path):
    data = base64.standard_b64encode(open(path, "rb").read()).decode()
    if path.lower().endswith(".pdf"):
        return {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": data}}
    mt = "image/png" if path.lower().endswith(".png") else "image/jpeg"
    return {"type": "image", "source": {"type": "base64", "media_type": mt, "data": data}}

def read_invoice(path):
    msg = client.messages.create(model="claude-sonnet-5-5", max_tokens=400,
        messages=[{"role": "user", "content": [block(path), {"type": "text", "text": ASK}]}],
        output_config={"format": {"type": "json_schema", "schema": SCHEMA}})
    inv = json.loads(msg.content[0].text)
    # never trust a number you can re-check: subtotal + VAT must equal the total
    inv["arithmetic_ok"] = abs(inv["subtotal"] + inv["vat"] - inv["total"]) < 0.02
    return inv, msg.usage.input_tokens

if __name__ == "__main__":
    print(read_invoice(sys.argv[1]))
