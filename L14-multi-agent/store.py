"""Mona Store data: 30 orders, 30 products, the return policy, and 10 customer messages that each ask 2-3 things at once.
Every part has one GOLD number that a correct answer must contain (tracking code, price, or number of days)."""
import random
random.seed(14)

CITIES = ["القاهرة", "الجيزة", "إسكندرية", "المنصورة", "طنطا", "أسيوط"]
STATUS = ["اتشحن", "بيتجهز", "اتسلم", "اتلغى"]
ORDERS = {}
for i, oid in enumerate(range(1031, 1061)):
    st = STATUS[i % 4] if i % 7 else "اتشحن"
    ORDERS[oid] = {"status": st, "city": CITIES[i % 6], "tracking": f"TRK-{random.randint(2000, 9899)}" if st in ("اتشحن", "اتسلم") else None,
                   "eta_days": random.randint(1, 4) if st == "اتشحن" else None}

PRODUCTS = [("شاحن 65 وات", 750), ("سماعة بلوتوث", 1290), ("باور بانك 20 ألف", 980), ("كابل تايب سي", 120), ("ماوس لاسلكي", 340),
            ("كيبورد ميكانيكال", 1850), ("ساعة ذكية", 2600), ("جراب موبايل", 95), ("سكرين بروتكشن", 60), ("حامل موبايل للعربية", 210),
            ("لمبة ذكية", 280), ("فلاشة 64 جيجا", 230), ("هارد خارجي 1 تيرا", 2350), ("سماعة سلك", 175), ("رينج لايت", 640),
            ("ستاند لابتوب", 520), ("مشترك كهربا", 260), ("كاميرا مراقبة", 1450), ("راوتر", 1990), ("مروحة USB", 150),
            ("ميكروفون", 890), ("شنطة لابتوب", 720), ("ماوس باد", 85), ("شاحن عربية", 190), ("سماعة رأس جيمنج", 1650),
            ("وصلة HDMI", 140), ("قلم تاتش", 330), ("ترايبود", 410), ("بطارية AA", 45), ("منظم كابلات", 70)]
PRICE = dict(PRODUCTS)

POLICY = """سياسة الاسترجاع في Mona Store:
- المنتجات العادية: تقدر ترجعها خلال 14 يوم من الاستلام لو مش مفتوحة.
- الإلكترونيات (شواحن، سماعات، باور بانك، ساعات، كاميرات، راوترات): خلال 7 أيام بس، ولازم تكون في علبتها.
- منتجات الأوكازيون (Sale): مفيش استرجاع، استبدال بس.
- الفلوس بترجع على نفس طريقة الدفع خلال 5 أيام عمل.
- أول استبدال شحنه مجاني، بعد كده 50 جنيه."""

def order_line(oid, o):
    return f"{oid} | {o['status']} | {o['city']} | " + (o["tracking"] or "-") + " | " + (f"يوصل خلال {o['eta_days']} يوم" if o["eta_days"] else "-")
ORDERS_TABLE = "الأوردرات (رقم | الحالة | المدينة | كود التتبع | الوصول):\n" + "\n".join(order_line(k, v) for k, v in ORDERS.items())
CATALOG_TABLE = "الأسعار (بالجنيه):\n" + "\n".join(f"{n}: {p}" for n, p in PRODUCTS)

def trk(oid): return ORDERS[oid]["tracking"].split("-")[1]

# (message, [(agent, gold), ...])
MESSAGES = [
    ("الأوردر 1031 فين؟ وكمان الشاحن 65 وات بكام؟", [("orders", trk(1031)), ("catalog", "750")]),
    ("عايزة أعرف كود التتبع بتاع 1035، وينفع أرجّع سماعة بلوتوث استلمتها من 3 أيام؟ ولحد كام يوم؟", [("orders", trk(1035)), ("returns", "7")]),
    ("الساعة الذكية بكام؟ والكيبورد الميكانيكال؟", [("catalog", "2600"), ("catalog", "1850")]),
    ("أوردري 1038 اتشحن ولا لسه؟ ابعتلي كود التتبع. ولو رجّعت حاجة الفلوس بترجع في كام يوم؟", [("orders", trk(1038)), ("returns", "5")]),
    ("جراب الموبايل بكام؟ ولو مش عاجبني أرجّعه خلال كام يوم؟ وكود تتبع الأوردر 1045 لو سمحت", [("catalog", "95"), ("returns", "14"), ("orders", trk(1045))]),
    ("الهارد الخارجي 1 تيرا بكام؟ وأوردر 1052 كود تتبعه إيه؟", [("catalog", "2350"), ("orders", trk(1052))]),
    ("لو استبدلت تاني مرة الشحن بكام؟ والراوتر سعره كام؟", [("returns", "50"), ("catalog", "1990")]),
    ("كود تتبع 1059 إيه؟ والميكروفون بكام؟ وأقدر أرجّع الباور بانك لحد كام يوم؟", [("orders", trk(1059)), ("catalog", "890"), ("returns", "7")]),
    ("عايز أعرف كود التتبع بتاع 1043، والرينج لايت بكام", [("orders", trk(1043)), ("catalog", "640")]),
    ("ستاند اللابتوب بكام؟ وشنطة اللابتوب؟ ولو رجعتهم الفلوس بترجع في كام يوم؟", [("catalog", "520"), ("catalog", "720"), ("returns", "5")]),
]

# ---------- BIG store: 5x the orders, 5x the products (same first 30 orders / products, same 10 messages) ----------
ORDERS_BIG = dict(ORDERS)
for i, oid in enumerate(range(1061, 1181)):
    st = STATUS[i % 4]
    ORDERS_BIG[oid] = {"status": st, "city": CITIES[i % 6], "tracking": f"TRK-{random.randint(2000, 9899)}" if st in ("اتشحن", "اتسلم") else None,
                       "eta_days": random.randint(1, 4) if st == "اتشحن" else None}
NOUNS = ["لمبة", "شنطة", "كابل", "حامل", "سماعة", "منظم", "ستاند", "علبة", "غطا", "ماوس", "لوحة", "مروحة"]
BRANDS = ["نوفا", "زيون", "ألفا", "تكنو", "سمارت لايف", "برو ماكس", "إيكو", "فلاش", "نيون", "أوربت"]
PRODUCTS_BIG = list(PRODUCTS) + [(f"{n} {b}", random.randint(4, 300) * 10 + 5) for n in NOUNS for b in BRANDS]
ORDERS_TABLE_BIG = "الأوردرات (رقم | الحالة | المدينة | كود التتبع | الوصول):\n" + "\n".join(order_line(k, v) for k, v in ORDERS_BIG.items())
CATALOG_TABLE_BIG = "الأسعار (بالجنيه):\n" + "\n".join(f"{n}: {p}" for n, p in PRODUCTS_BIG)

if __name__ == "__main__":
    for m, parts in MESSAGES:
        print(m, parts)
    print(len(ORDERS_TABLE) + len(CATALOG_TABLE) + len(POLICY), "chars of data;  big:", len(ORDERS_TABLE_BIG) + len(CATALOG_TABLE_BIG) + len(POLICY), len(ORDERS_BIG), len(PRODUCTS_BIG))
    for oid in (1031, 1032, 1035, 1038, 1045, 1052, 1059): print(oid, ORDERS[oid])
