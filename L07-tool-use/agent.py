from client import client, MODEL
from mona import SYSTEM_TOOLS
from tools import TOOLS, run_tool

def ask(question, tools=TOOLS, system=SYSTEM_TOOLS, trace=True):
    messages = [{"role": "user", "content": question}]
    while True:
        msg = client.messages.create(
            model=MODEL, max_tokens=400, system=system,
            thinking={"type": "disabled"},
            messages=messages, **({"tools": tools} if tools else {}))
        messages.append({"role": "assistant", "content": msg.content})
        if msg.stop_reason != "tool_use":          # the model answered: done
            return "".join(b.text for b in msg.content if b.type == "text"), messages
        results = []
        for block in msg.content:                  # the model asked for one or more tools
            if block.type == "tool_use":
                out = run_tool(block.name, block.input)
                if trace: print(f"  -> {block.name}({block.input}) = {out}")
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": out})
        messages.append({"role": "user", "content": results})

if __name__ == "__main__":
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "الأوردر 1042 وصل فين؟"
    print("Q:", q)
    a, _ = ask(q)
    print("Mona:", a)
