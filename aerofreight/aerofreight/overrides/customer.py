import frappe
from frappe.utils import getdate, today

def validate(doc, method=None):
    if doc.disabled:
        return

    current_date = getdate(today())

    for kyc in doc.custom_kyc:
        if kyc.date and getdate(kyc.date) <= current_date:
            frappe.throw(
                f"Customer cannot be enabled. KYC document '{kyc.document}' "
                f"expired on {kyc.date}. Please update the KYC expiry date."
            )