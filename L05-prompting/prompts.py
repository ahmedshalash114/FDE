LABELS = "refund, exchange, shipping, cancel, payment, damaged, warranty, account, error, support"

V1 = "صنّف الرسالة دي: {msg}"                                   # vague

V2 = ("Classify the customer message into exactly one label: " + LABELS + ".\n"
      "Reply with the label only.\n\nMessage: {msg}")             # clear & direct

V3 = """Classify the customer message into exactly one label.
<labels>
refund: wants the money back
exchange: wants another size or color
shipping: asks when or where the order arrives
cancel: does not want the order anymore
payment: how to pay, cards, installments
damaged: the product arrived broken or missing
warranty: a device stopped working by itself
account: login, password, phone number
error: an error code like TS-500
support: wants to reach a human or the hotline
</labels>
<message>{msg}</message>
Reply with the label only."""                                 # specific + XML tags

V4 = V3.replace("Reply with the label only.", """<examples>
<message>الفلوس هترجعلي إمتى؟</message> refund
<message>الشاشة جاتلي مشروخة</message> damaged
<message>عايز أكلم حد من خدمة العملاء</message> support
</examples>
Reply with the label only.""")                                  # + examples
