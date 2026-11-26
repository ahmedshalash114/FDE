"""The same extraction on Claude: the schema is enforced by the API (JSON outputs), or by the SDK with a Pydantic model."""
from typing import Literal, Optional
from anthropic import Anthropic
from pydantic import BaseModel
from schema import SCHEMA
from extract import SYSTEM

client = Anthropic()
MODEL = "claude-haiku-4-5"

# 1) raw JSON schema -> output_config.format
msg = client.messages.create(
    model=MODEL, max_tokens=200, system=SYSTEM,
    messages=[{"role": "user", "content": "الغوا الأوردر 1060 بسرعة لو سمحتم قبل ما يتشحن!!"}],
    output_config={"format": {"type": "json_schema", "schema": SCHEMA}})
print(msg.content[0].text)        # always valid JSON that matches SCHEMA

# 2) Pydantic model -> parsed object
class Ticket(BaseModel):
    order_id: Optional[int]
    intent: Literal["status", "refund", "cancel", "complaint", "other"]
    urgent: bool

res = client.messages.parse(model=MODEL, max_tokens=200, system=SYSTEM, output_format=Ticket,
                            messages=[{"role": "user", "content": "فلوس المرتجع بتاع 1045 لسه مرجعتش ليه؟"}])
print(res.parsed_output)          # Ticket(order_id=1045, intent='refund', urgent=False)

# Tools too: add "strict": True to a tool definition and its input always matches input_schema.
