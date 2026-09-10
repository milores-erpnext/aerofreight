import copy
import frappe

from erpnext.accounts.report.customer_ledger_summary.customer_ledger_summary import (
    execute as original_execute,
)
from erpnext.accounts.report.accounts_receivable_summary.accounts_receivable_summary import (
    execute as ar_summary_execute,
)


def execute(filters=None):
    columns, data = original_execute(filters)

    # -----------------------------
    # Credit Limit & Credit Days
    # -----------------------------
    territory_idx = next(
        (i for i, c in enumerate(columns) if c.get("fieldname") == "territory"),
        len(columns),
    )

    columns.insert(
        territory_idx + 1,
        {
            "label": "Credit Limit",
            "fieldname": "credit_limit",
            "fieldtype": "Currency",
            "width": 130,
        },
    )

    columns.insert(
        territory_idx + 2,
        {
            "label": "Credit Days",
            "fieldname": "custom_customer_credit_days_",
            "fieldtype": "Int",
            "width": 110,
        },
    )

    columns.insert(
        territory_idx + 3,
        {
            "label": "Sales Person",
            "fieldname": "sales_person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 180,
        },
    )

    # -----------------------------
    # Ageing Columns
    # -----------------------------
    ageing_columns = [
        {"label": "120 Above", "fieldname": "range5", "fieldtype": "Currency", "width": 120},
        {"label": "91 - 120", "fieldname": "range4", "fieldtype": "Currency", "width": 110},
        {"label": "61 - 90", "fieldname": "range3", "fieldtype": "Currency", "width": 110},
        {"label": "31 - 60", "fieldname": "range2", "fieldtype": "Currency", "width": 110},
        {"label": "0 - 30", "fieldname": "range1", "fieldtype": "Currency", "width": 110},
        {"label": "< 0", "fieldname": "range0", "fieldtype": "Currency", "width": 110},
    ]

    for col in ageing_columns:
        columns.insert(territory_idx + 4, (col))

    if not data:
        return columns, data

    company = filters.get("company") if filters else None
    customers = [d.get("party") for d in data if d.get("party")]

    # -----------------------------
    # Credit Limit Mapping
    # -----------------------------
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
        credit_days_map = {
            d.parent: d.custom_customer_credit_days_ for d in records
        }

    # -----------------------------
    # Fetch AR Summary Ageing
    # -----------------------------
    ar_filters = copy.deepcopy(filters or {})
    _, ar_data = ar_summary_execute(ar_filters)

    ageing_map = {}
    for row in ar_data:
        ageing_map[row.get("party")] = {
            "range0": row.get("range0", 0),
            "range1": row.get("range1", 0),
            "range2": row.get("range2", 0),
            "range3": row.get("range3", 0),
            "range4": row.get("range4", 0),
            "range5": row.get("range5", 0),
        }

    # -----------------------------
    # Sales Person Mapping
    # -----------------------------
    sales_person_map = {}

    if customers:
        sales_team = frappe.get_all(
            "Sales Team",
            filters={"parent": ["in", customers], "parenttype": "Customer"},
            fields=["parent", "sales_person"],
            order_by="idx asc",
            ignore_permissions=True,
        )

        # Take first sales person for each customer
        for d in sales_team:
            sales_person_map.setdefault(d.parent, d.sales_person)

    # -----------------------------
    # Update Customer Ledger Summary rows
    # -----------------------------
    for row in data:
        party = row.get("party")

        row["credit_limit"] = credit_limit_map.get(party, 0)
        row["custom_customer_credit_days_"] = credit_days_map.get(party, 0)
        row["sales_person"] = sales_person_map.get(party, None)

        ageing = ageing_map.get(party, {})
        row["range0"] = ageing.get("range0", 0)
        row["range1"] = ageing.get("range1", 0)
        row["range2"] = ageing.get("range2", 0)
        row["range3"] = ageing.get("range3", 0)
        row["range4"] = ageing.get("range4", 0)
        row["range5"] = ageing.get("range5", 0)

    return columns, data