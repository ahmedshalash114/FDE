import sqlite3

ORDERS = [  # id, item, status, eta, refund
    (1042, "سماعة بلوتوث", "processing", None, None),
    (1043, "شاحن 65 وات", "shipped", "2026-11-25", None),
    (1044, "كيبورد", "delivered", "2026-11-20", None),
    (1045, "ماوس", "returned", None, "refund in progress, 5 to 7 working days from 2026-11-18"),
    (1046, "شاشة 27 بوصة", "cancelled", None, "refunded on 2026-11-21"),
]

def build(path="orders.db"):
    db = sqlite3.connect(path)
    db.execute("DROP TABLE IF EXISTS orders")
    db.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, item TEXT, status TEXT, eta TEXT, refund TEXT)")
    db.executemany("INSERT INTO orders VALUES (?,?,?,?,?)", ORDERS)
    db.commit()
    return db

if __name__ == "__main__":
    build(); print("orders.db ready:", len(ORDERS), "orders")
