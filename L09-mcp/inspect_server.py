"""Connect to the MCP server and print what a client sees: tools (with the generated schemas) and resources."""
import asyncio, json, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = StdioServerParameters(command=sys.executable, args=["mcp_server.py"])

async def main():
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            for t in (await session.list_tools()).tools:
                print("TOOL", t.name, "-", t.description)
                print("     input_schema:", json.dumps(t.input_schema))
            for r in (await session.list_resources()).resources:
                print("RESOURCE", r.uri, "-", r.description)
            res = await session.call_tool("get_order", {"order_id": 1046})
            print("CALL get_order(1046) ->", res.content[0].text)

asyncio.run(main())
