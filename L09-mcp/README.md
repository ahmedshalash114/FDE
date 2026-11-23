# L09 · MCP — الـ tools بتاعة منى بقت server

الكود بتاع الدرس التاسع من سلسلة **FDE Academy**، على قسم *Model Context Protocol* في كورس Anthropic Academy
*Building with the Claude API*: Introducing MCP → MCP clients → Defining tools with MCP → Implementing a client → Defining / accessing resources.

- `mcp_server.py`: MCP server (Python SDK `mcp>=2`، `MCPServer`) فيه نفس الـ tools بتاعة L07: `get_order` و `get_refund` + resource اسمه `orders://policy`.
  الـ docstring بيبقى الـ description، والـ `input_schema` بيتولّد من الـ type hints.
  (لو عندك `mcp` 1.x: `from mcp.server.fastmcp import FastMCP` بدل `MCPServer`.)
- `inspect_server.py`: يتوصّل بالـ server ويطبع اللي أي client هيشوفه (tools + schemas + resources) ويجرّب `call_tool`.
- `mcp_agent.py`: منى كـ MCP client: `stdio_client` → `ClientSession` → `list_tools` → Claude، و `call_tool` لما الموديل يطلب. الـ policy جاية من `read_resource`.
- `mcp_eval.py`: نفس الست أسئلة والـ grader من L07، بس الـ tools من الـ server.

## شغّله

```bash
ollama pull qwen3.5:4b
pip install -r requirements.txt
python db.py
python inspect_server.py
python mcp_agent.py "الأوردر 1042 وصل فين؟"
python mcp_eval.py
```

عايز Claude؟ في `client.py`: `client = Anthropic()` و `MODEL = "claude-haiku-4-5"`.

نفس الـ server في Claude Desktop — في `claude_desktop_config.json`:

```json
{"mcpServers": {"orders": {"command": "python", "args": ["/full/path/to/mcp_server.py"]}}}
```

## النتايج الحقيقية (qwen3.5:4b على Ollama، اتشغّلت مرة واحدة)

```
TOOL get_order - Look up one order in the store database: item, status (...) and delivery date (eta).
     input_schema: {"properties": {"order_id": {"title": "Order Id", "type": "integer"}}, "required": ["order_id"], "type": "object", "title": "get_orderArguments"}
RESOURCE orders://policy - The store's refund policy.

$ python mcp_agent.py "الأوردر 1042 وصل فين؟"
  -> MCP get_order({'order_id': 1042}) = {"order_id": 1042, "item": "سماعة بلوتوث", "status": "processing", "eta": null}
Mona: الأمر ما يزال في مرحلة تجهيز الشحنة.
```

| | tool calls | مراجعة بإيدي |
|---|---|---|
| L07 · الـ tools جوّه الكود (schema مكتوب بإيدي) | 5/6 | 3/6 |
| L09 · نفس الـ tools عبر MCP (schema متولّد) | 4/6 | 3/6 |

- **1046:** «أهلاً يا حبيبي! دعني أتحقق من حالة الأوردر 1046 وحالة الإرجاع فوراً.» — ومنادتش أي tool.
- **1043:** نادت الـ tool (eta = 2026-11-25، يوم أربع) وقالت «هتوصل يوم الخميس».
- **الـ grader:** في 1042 كتب *"...which matches, so it is a match."* وحط `"pass": false` (الـ grader قال 2/6، بإيدي 3/6).
- **الدرس:** MCP بيخلّي الـ tools تتركّب في أي مكان، بس مش بيخلّي الموديل أذكى. أي تغيير (حتى في الـ schema) → عيد الـ eval.

الحلقة الجاية والأخيرة: **L10 · Agents**.
