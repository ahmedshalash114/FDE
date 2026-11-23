from client import chat

q = [{"role": "user", "content": "عايز فلوسي ترجع"}]
print("generic:", chat(q))        # default: "You are a helpful assistant."

SYSTEM = """إنت موظف خدمة عملاء في متجر إلكتروني مصري.
رد بالعامية المصرية، في جملتين بالكتير.
لو العميل عايز يرجّع حاجة، اطلب رقم الأوردر."""
print("ours   :", chat(q, system=SYSTEM))
