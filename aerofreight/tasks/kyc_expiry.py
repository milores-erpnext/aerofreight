import frappe
from frappe.utils import nowdate

def send_kyc_expiry_assignments():
    customers = frappe.get_all(
        "Customer", 
        filters={"disabled": 0},
        fields=["name"]
    )

    for customer in customers:
        customer_doc = frappe.get_doc("Customer", customer.name)
        if customer_doc.custom_kyc:
            for sp in customer_doc.sales_team:
                emp = frappe.db.get_value("Sales Person", sp.sales_person, "employee")
                employee_doc = frappe.get_doc("Employee",emp)
                if employee_doc.user_id:
                    get_kyc_expiry_todos(employee_doc.user_id,customer_doc.custom_kyc[0].name,customer_doc.name)
                if employee_doc.reports_to:
                    reports_to_doc = frappe.get_doc("Employee",employee_doc.reports_to)
                    if reports_to_doc.user_id:
                        get_kyc_expiry_todos(reports_to_doc.user_id,customer_doc.custom_kyc[0].name,customer_doc.name)
                if employee_doc.company:
                    aero_mail_id = frappe.get_value("Asset Manager Alignment",{"company": employee_doc.company},"user")
                    if aero_mail_id:
                        get_kyc_expiry_todos(aero_mail_id,customer_doc.custom_kyc[0].name,customer_doc.name)

def get_kyc_expiry_todos(assignee, reference_name,customer_name):
    d = frappe.get_doc(
        {
            "doctype": "ToDo",
            "allocated_to": assignee,
            "reference_type": "Customer",
            "reference_name": customer_name,
            "description": customer_name + " KYC is expiring soon. Please take necessary action.",
            "priority": "Medium",
            "status": "Open",
            "date": nowdate(),
            "assigned_by": "Administrator",
        }
    ).insert(ignore_permissions=True)
