from anthropic import Anthropic

# Claude: client = Anthropic()  and  MODEL = "claude-haiku-4-5"
client = Anthropic(base_url="http://localhost:11434", api_key="ollama")
MODEL = "qwen3.5:4b"

def chat(messages, system="You are a helpful assistant."):
    msg = client.messages.create(
        model=MODEL, max_tokens=300, system=system,
        thinking={"type": "disabled"},
        messages=messages)
    return msg.content[0].text
