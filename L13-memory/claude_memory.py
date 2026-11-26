"""The same idea on Claude, with the built-in memory tool.

Claude decides what to save and when; YOUR code stores the files (client-side), so you keep control:
one folder per customer, and you can read, audit or wipe it any time.
Docs: https://docs.claude.com/en/docs/agents-and-tools/tool-use/memory-tool

Needs ANTHROPIC_API_KEY.   python claude_memory.py
"""
import os, shutil
from pathlib import Path
import anthropic

client = anthropic.Anthropic()
MODEL = "claude-sonnet-5-5"
ROOT = Path("claude_memories")          # what Claude calls /memories lives here, one folder per customer

SYSTEM = ("You are Mona, the support agent of Mona Store (Egypt). Answer in Egyptian Arabic, in at most two short sentences. "
          "Save only what the CUSTOMER said (order ids, city, contact preference, payment, constraints). "
          "Never save your own promises or guesses as facts.")


def safe(customer, path):               # never let a path escape the customer's folder
    base = (ROOT / customer).resolve()
    p = (base / path.removeprefix("/memories").lstrip("/")).resolve()
    if base != p and base not in p.parents:
        raise ValueError(f"path outside memory dir: {path}")
    return p


def run_memory(customer, cmd):          # the six commands of the memory tool, implemented by us
    c = cmd["command"]; p = safe(customer, cmd.get("path", "/memories"))
    if c == "view":
        if p.is_dir():
            return "\n".join(str(f.relative_to(ROOT / customer)) for f in sorted(p.rglob("*")) if f.is_file()) or "(empty)"
        return "\n".join(f"{i + 1}\t{l}" for i, l in enumerate(p.read_text().splitlines())) if p.exists() else f"No such file: {cmd['path']}"
    if c == "create":
        p.parent.mkdir(parents=True, exist_ok=True); p.write_text(cmd["file_text"]); return f"Created {cmd['path']}"
    if c == "str_replace":
        s = p.read_text()
        if s.count(cmd["old_str"]) != 1: return "Error: old_str must appear exactly once"
        p.write_text(s.replace(cmd["old_str"], cmd["new_str"])); return "Edited"
    if c == "insert":
        lines = p.read_text().splitlines(); lines.insert(cmd["insert_line"], cmd["insert_text"]); p.write_text("\n".join(lines)); return "Inserted"
    if c == "delete":
        shutil.rmtree(p) if p.is_dir() else p.unlink(); return "Deleted"
    if c == "rename":
        p.rename(safe(customer, cmd["new_path"])); return "Renamed"
    return f"Unknown command {c}"


def talk(customer, text):
    """One customer turn. Claude checks /memories first (it is told to by the tool), may save, then answers."""
    messages = [{"role": "user", "content": text}]
    while True:
        msg = client.beta.messages.create(
            model=MODEL, max_tokens=600, system=SYSTEM, messages=messages,
            tools=[{"type": "memory_20250818", "name": "memory"}],
            # long agent runs: let the API drop old tool results, the memory files keep what matters
            context_management={"edits": [{"type": "clear_tool_uses_20250919", "trigger": {"type": "input_tokens", "value": 30000},
                                           "keep": {"type": "tool_uses", "value": 3}}]},
            betas=["context-management-2025-06-27"])
        messages.append({"role": "assistant", "content": msg.content})
        calls = [b for b in msg.content if b.type == "tool_use"]
        if not calls:
            return "".join(b.text for b in msg.content if b.type == "text")
        messages.append({"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": b.id, "content": run_memory(customer, b.input)} for b in calls]})


if __name__ == "__main__":
    print("day 1:", talk("Nour", "أوردري 1042، وأي تحديث ابعتوهولي على واتساب، مش بحب المكالمات"))
    print("saved:", *(f.read_text() for f in (ROOT / "Nour").rglob("*") if f.is_file()))
    print("day 2:", talk("Nour", "ابقوا بلغوني لما يتشحن"))      # a NEW conversation: only the memory files carry over
