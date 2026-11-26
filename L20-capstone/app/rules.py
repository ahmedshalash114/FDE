"""The model asks, the code decides (L15). Every action that touches money or an order is decided here, never by the model."""
import re
from .data import ORDERS, RETURN_DAYS

AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
def order_id(text: str) -> str | None:
    """The number right after أوردر / طلب / order wins. ("رجّعولي 5000 جنيه عن أوردر 1051" -> 1051, not 5000: a test caught that.)"""
    t = text.translate(AR_DIGITS)
    m = re.search(r"(?:أوردر|اوردر|الأوردر|الاوردر|طلب|الطلب|طلبي|order)\D{0,8}(\d{4})\b", t, re.I) or re.search(r"\b(\d{4})\b", t)
    return m.group(1) if m else None

def _own(oid, customer):
    o = ORDERS.get(oid)
    if not o: return None, "not_found"
    if o["customer"] != customer: return None, "not_yours"
    return o, None

def refund(oid, customer) -> dict:
    o, err = _own(oid, customer)
    if err: return {"action": "refund_denied", "reason": err}
    if o["status"] != "delivered": return {"action": "refund_denied", "reason": "not_delivered_yet"}
    if o["delivered_days_ago"] > RETURN_DAYS: return {"action": "refund_denied", "reason": f"after_{RETURN_DAYS}_days"}
    return {"action": "refund_approved", "amount": o["total"]}          # the amount comes from the order, never from the message

def cancel(oid, customer) -> dict:
    o, err = _own(oid, customer)
    if err: return {"action": "cancel_denied", "reason": err}
    if o["status"] != "processing": return {"action": "cancel_denied", "reason": "already_shipped"}
    return {"action": "cancel_done"}

def status(oid, customer) -> dict:
    o, err = _own(oid, customer)
    return {"action": "none", "reason": err} if err else {"action": "none", "status": o["status"], "item": o["item"]}
