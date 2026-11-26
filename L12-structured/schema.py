SCHEMA = {
    "type": "object",
    "properties": {
        "order_id": {"type": ["integer", "null"], "description": "the order number, or null if there is none"},
        "intent":   {"type": "string", "enum": ["status", "refund", "cancel", "complaint", "other"]},
        "urgent":   {"type": "boolean", "description": "true if the customer needs it now / is angry / is in a hurry"},
    },
    "required": ["order_id", "intent", "urgent"],
    "additionalProperties": False,
}
INTENTS = SCHEMA["properties"]["intent"]["enum"]

def schema_errors(d):
    """Tiny validator for SCHEMA (no extra dependency). Returns a list of problems."""
    if not isinstance(d, dict): return ["not an object"]
    errs = []
    for k in SCHEMA["required"]:
        if k not in d: errs.append(f"missing {k}")
    for k in d:
        if k not in SCHEMA["properties"]: errs.append(f"extra key {k}")
    if "order_id" in d and not (d["order_id"] is None or (isinstance(d["order_id"], int) and not isinstance(d["order_id"], bool))):
        errs.append(f"order_id is {type(d['order_id']).__name__}")
    if "intent" in d and d["intent"] not in INTENTS: errs.append(f"intent={d['intent']!r}")
    if "urgent" in d and not isinstance(d["urgent"], bool): errs.append(f"urgent is {type(d['urgent']).__name__}")
    return errs
