import frappe
from erpnext.accounts.report.customer_ledger_summary.customer_ledger_summary import (
    execute as original_execute,
)


def execute(filters=None):
    columns, data = original_execute(filters)

    # Insert new columns after Territory
    territory_idx = next(
        (i for i, c in enumerate(columns) if c.get("fieldname") == "territory"),
        len(columns),
    )
    columns.insert(territory_idx + 1, {
        "label": "Credit Limit",
        "fieldname": "credit_limit",
        "fieldtype": "Currency",
        "width": 130,
    })
    columns.insert(territory_idx + 2, {
        "label": "Credit Days",
        "fieldname": "custom_customer_credit_days_",
        "fieldtype": "Int",
        "width": 100,
    })

    if not data:
        return columns, data

    company = filters.get("company") if filters else None
    customers = [d.get("party") for d in data if d.get("party")]

    credit_limit_map = {}
    credit_days_map = {}

    if customers:
        cc_filters = {"parent": ["in", customers]}
        if company:
            cc_filters["company"] = company

        records = frappe.get_all(
            "Customer Credit Limit",
            filters=cc_filters,
            fields=["parent", "credit_limit", "custom_customer_credit_days_"],
            ignore_permissions=True,
        )
        credit_limit_map = {d.parent: d.credit_limit for d in records}
        credit_days_map = {d.parent: d.custom_customer_credit_days_ for d in records}

    for row in data:
        party = row.get("party")
        row["credit_limit"] = credit_limit_map.get(party, 0)
        row["custom_customer_credit_days_"] = credit_days_map.get(party, 0)

    return columns, data