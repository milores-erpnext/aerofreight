import frappe
from frappe import _


@frappe.whitelist()
def get_accounts_manager_for_custodian(custodian):
    """
    Given an Asset's custodian (Employee), resolve the Accounts Manager user
    based on the Employee's Company and the Asset Manager Alignment table
    in Aero Settings. Returns a dict with the user and their full name.
    """
    if not custodian:
        return {"user": "", "full_name": ""}

    company = frappe.db.get_value("Employee", custodian, "company")
    if not company:
        return {"user": "", "full_name": ""}

    settings = frappe.get_single("Aero Settings")

    alignment_user = None
    for row in settings.asset_manager_alignment or []:
        if row.company == company:
            alignment_user = row.user
            break

    if not alignment_user:
        return {"user": "", "full_name": ""}

    full_name = frappe.db.get_value("User", alignment_user, "full_name") or ""

    return {"user": alignment_user, "full_name": full_name}