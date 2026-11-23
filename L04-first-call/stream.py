from client import client, MODEL

with client.messages.stream(
        model=MODEL, max_tokens=200,
        thinking={"type": "disabled"},
        messages=[{"role": "user", "content": "اشرح الـ API في جملة واحدة"}]) as stream:
    for text in stream.text_stream:          # words arrive as they are generated
        print(text, end="|", flush=True)
