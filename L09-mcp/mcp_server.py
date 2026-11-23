"""Mona's order tools as an MCP server. Any MCP client can use them: our Python client, Claude Desktop, Claude Code..."""
import sqlite3
from mcp.server.mcpserver import MCPServer      # mcp >= 2  (mcp 1.x: from mcp.server.fastmcp import FastMCP)

server = MCPServer("orders")
db = sqlite3.connect("orders.db", check_same_thread=False)

POLICY = """Full refund within 14 days of delivery if the product is unused.
The money goes back to the same payment method in 5 to 7 working days."""


@server.tool()
def get_order(order_id: int) -> dict:
    """Look up one order in the store database: item, status (processing, shipped, delivered, returned, cancelled) and delivery date (eta)."""
    row = db.execute("SELECT id, item, status, eta FROM orders WHERE id = ?", (order_id,)).fetchone()
    if row is None:
        return {"error": f"order {order_id} not found"}
    return {"order_id": row[0], "item": row[1], "status": row[2], "eta": row[3]}


@server.tool()
def get_refund(order_id: int) -> dict:
    """Look up the refund status of one order."""
    row = db.execute("SELECT refund FROM orders WHERE id = ?", (order_id,)).fetchone()
    if row is None:
        return {"error": f"order {order_id} not found"}
    return {"order_id": order_id, "refund": row[0] or "no refund on this order"}


@server.resource("orders://policy")
def policy() -> str:
    """The store's refund policy."""
    return POLICY


if __name__ == "__main__":
    server.run()          # stdio
