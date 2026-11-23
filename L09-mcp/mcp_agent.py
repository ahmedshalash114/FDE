"""Mona as an MCP client: tools and the policy come from the MCP server, not from our code."""
import asyncio, json, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from client import client, MODEL

SERVER = StdioServerParameters(command=sys.executable, args=["mcp_server.py"])

SYSTEM = """You are Mona, a customer-support agent for an Egyptian online store. Today is 2026-11-23.
<rules>
- Write in Egyptian Arabic (عامية مصرية), never formal Arabic.
- At most two short sentences. No lists, no markdown, no emojis.
- Use only the policy below and facts you looked up. Never guess an order's status or date.
- Never promise a day or a time. Refunds take 5 to 7 working days.
- Before you answer anything about an order, call get_order. If there is a refund question, also call get_refund.
</rules>
<policy>
{policy}
</policy>"""


async def connect(stack):
    read, write = await stack.enter_async_context(stdio_client(SERVER))
    session = await stack.enter_async_context(ClientSession(read, write))
    await session.initialize()
    tools = [{"name": t.name, "description": t.description, "input_schema": t.input_schema}
             for t in (await session.list_tools()).tools]                              # MCP tools -> Claude tools
    policy = (await session.read_resource("orders://policy")).contents[0].text         # MCP resource -> system prompt
    return session, tools, SYSTEM.format(policy=policy)


async def ask(session, tools, system, question, trace=True):
    messages = [{"role": "user", "content": question}]
    while True:
        msg = client.messages.create(model=MODEL, max_tokens=400, system=system,
                                     thinking={"type": "disabled"}, tools=tools, messages=messages)
        messages.append({"role": "assistant", "content": msg.content})
        if msg.stop_reason != "tool_use":
            return "".join(b.text for b in msg.content if b.type == "text"), messages
        results = []
        for b in msg.content:
            if b.type == "tool_use":
                out = await session.call_tool(b.name, b.input)                         # the MCP server runs it
                text = out.content[0].text
                if trace: print(f"  -> MCP {b.name}({b.input}) = {json.dumps(json.loads(text), ensure_ascii=False)}")
                results.append({"type": "tool_result", "tool_use_id": b.id, "content": text})
        messages.append({"role": "user", "content": results})


async def main(q):
    from contextlib import AsyncExitStack
    async with AsyncExitStack() as stack:
        session, tools, system = await connect(stack)
        print("tools from the server:", [t["name"] for t in tools])
        print("Q:", q)
        reply, _ = await ask(session, tools, system, q)
        print("Mona:", reply)

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "لغيت أوردر 1046، الفلوس رجعت؟"))
