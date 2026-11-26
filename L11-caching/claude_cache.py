"""The same thing on Claude: mark the stable prefix with cache_control and read the cache counters."""
from anthropic import Anthropic
from handbook import HANDBOOK

client = Anthropic()            # ANTHROPIC_API_KEY
MODEL = "claude-haiku-4-5"      # note: Haiku 4.5 only caches prompts of 4,096+ tokens

def ask(name, question):
    msg = client.messages.create(
        model=MODEL, max_tokens=300,
        system=[
            {"type": "text", "text": HANDBOOK, "cache_control": {"type": "ephemeral"}},  # stable -> cached (5 min)
            {"type": "text", "text": f"Today is Wednesday 26 Nov 2026. Customer name: {name}."},  # changes -> after the breakpoint
        ],
        messages=[{"role": "user", "content": question}])
    u = msg.usage
    print("write:", u.cache_creation_input_tokens, "read:", u.cache_read_input_tokens, "uncached:", u.input_tokens)
    return msg.content[0].text

# Or let the API place the breakpoint for you (automatic caching):
#   client.messages.create(..., cache_control={"type": "ephemeral"}, system=..., messages=...)

if __name__ == "__main__":
    print(ask("Sara", "رجّعت سماعة من 4 أيام، الفلوس هترجع إمتى؟"))   # first call  -> write
    print(ask("Omar", "عايز أرجّع جاكيت، في رسوم؟"))                  # second call -> read (10% of the price)
