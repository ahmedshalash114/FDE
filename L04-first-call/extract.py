import json
from client import client, MODEL

text = "الأوردر 1042 وصلني مكسور وده تالت مرة!! عايز فلوسي"

msg = client.messages.create(
    model=MODEL, max_tokens=200,
    thinking={"type": "disabled"},
    messages=[
        {"role": "user", "content": "Extract JSON with keys intent, order_id, "
                                    f"angry (true/false) from:\n{text}"},
        {"role": "assistant", "content": "```json"}],   # prefill
    stop_sequences=["```"])

data = json.loads(msg.content[0].text)
print(data)
print(type(data["angry"]), data["order_id"])
