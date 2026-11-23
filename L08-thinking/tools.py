import json, sqlite3

db = sqlite3.connect("orders.db")

# 1) the tool function: plain Python
def get_order(order_id):
    row = db.execute("SELECT id, item, status, eta FROM orders WHERE id = ?", (order_id,)).fetchone()
    if row is None:
        return {"error": f"order {order_id} not found"}
    return {"order_id": row[0], "item": row[1], "status": row[2], "eta": row[3]}

def get_refund(order_id):
    row = db.execute("SELECT refund FROM orders WHERE id = ?", (order_id,)).fetchone()
    if row is None:
        return {"error": f"order {order_id} not found"}
    return {"order_id": order_id, "refund": row[0] or "no refund on this order"}

# 2) the tool schema: what the model sees
TOOLS = [
    {"name": "get_order",
     "description": "Look up one order in the store database: item, status "
                    "(processing, shipped, delivered, returned, cancelled) and delivery date (eta).",
     "input_schema": {"type": "object",
                      "properties": {"order_id": {"type": "integer", "description": "The order number, e.g. 1042"}},
                      "required": ["order_id"]}},
    {"name": "get_refund",
     "description": "Look up the refund status of one order.",
     "input_schema": {"type": "object",
                      "properties": {"order_id": {"type": "integer"}},
                      "required": ["order_id"]}},
]
FUNCS = {"get_order": get_order, "get_refund": get_refund}

def run_tool(name, args):
    return json.dumps(FUNCS[name](**args), ensure_ascii=False)
