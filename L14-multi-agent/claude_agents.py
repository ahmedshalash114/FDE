"""Orchestrator + workers on Claude: the plan comes back as JSON (structured outputs, L12),
the workers run in PARALLEL (asyncio), each one sees only its own data, then a writer merges.
Needs ANTHROPIC_API_KEY.   python claude_agents.py
"""
import asyncio, json
from anthropic import AsyncAnthropic
from agents import WORKERS, ORCH, WRITER, PLAN_SCHEMA
from store import MESSAGES

client = AsyncAnthropic()
SMALL, BIG = "claude-haiku-5-5", "claude-sonnet-5-5"     # cheap model for workers, stronger one to plan

async def ask(model, system, user, schema=None):
    kw = {"output_config": {"format": {"type": "json_schema", "schema": schema}}} if schema else {}
    msg = await client.messages.create(model=model, max_tokens=500, system=system, messages=[{"role": "user", "content": user}], **kw)
    return msg.content[0].text

async def handle(customer_msg):
    plan = json.loads(await ask(BIG, ORCH, customer_msg, PLAN_SCHEMA))["tasks"]
    answers = await asyncio.gather(*(ask(SMALL, WORKERS[t["agent"]], t["question"]) for t in plan))   # parallel
    team = "\n".join(f"- ({t['agent']}) {t['question']}\n  {a}" for t, a in zip(plan, answers))
    return await ask(SMALL, WRITER, f"Customer message:\n{customer_msg}\n\nTeam answers:\n{team}")

if __name__ == "__main__":
    for m, _ in MESSAGES[:3]:
        print(m, "\n->", asyncio.run(handle(m)), "\n")
