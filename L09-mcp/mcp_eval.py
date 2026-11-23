"""L07's 6 questions again, but every tool now lives in the MCP server."""
import asyncio, json
from contextlib import AsyncExitStack
from mcp_agent import connect, ask
import eval_l07 as L07

async def main():
    rows = []
    async with AsyncExitStack() as stack:
        session, tools, system = await connect(stack)
        for oid, q in L07.QUESTIONS:
            truth = L07.TRUTH.get(oid, {"order_id": oid, "error": "order not found"})
            reply, messages = await ask(session, tools, system, q, trace=False)
            calls = [b.name + str(b.input) for m in messages if m["role"] == "assistant" for b in m["content"] if b.type == "tool_use"]
            g = L07.grade(q, reply, truth) if reply.strip() else {"reason": "no reply", "pass": False}
            rows.append({"q": q, "reply": reply, "calls": calls, **g})
            print(f"{q[:26]:26s} | {'PASS' if g['pass'] else 'FAIL'} | calls {len(calls)} | {reply[:70]!r}")
    print(f"== via MCP: {sum(r['pass'] for r in rows)}/{len(rows)} correct · tool calls in {sum(bool(r['calls']) for r in rows)}/{len(rows)}")
    json.dump(rows, open("results.json", "w"), ensure_ascii=False, indent=1)

asyncio.run(main())
