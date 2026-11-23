from client import chat

hi = {"role": "user", "content": "أنا اسمي أحمد"}
reply = chat([hi])
print("1:", reply)

# a new request = a new conversation: the API keeps no memory
print("2:", chat([{"role": "user", "content": "اسمي إيه؟"}]))

# so we send the whole history every time
history = [hi, {"role": "assistant", "content": reply},
           {"role": "user", "content": "اسمي إيه؟"}]
print("3:", chat(history))
