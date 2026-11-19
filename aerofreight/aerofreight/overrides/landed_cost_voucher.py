
import frappe
from frappe.utils import flt
from erpnext.stock.doctype.landed_cost_voucher.landed_cost_voucher import (
    LandedCostVoucher as ERPNextLandedCostVoucher,
)


class CustomLandedCostVoucher(ERPNextLandedCostVoucher):

    def set_applicable_charges_on_item(self):

        items = self.get("items")
        taxes = self.get("taxes")

        if not taxes or not items:
            return

        # Reset existing allocation
        for item in items:
            item.applicable_charges = 0

        total_allocated = 0

        for tax_index, tax in enumerate(taxes):

            basis = (tax.custom_allocation_basis or "").strip().lower()
            tax_amount = flt(tax.base_amount)

            if not tax_amount:
                continue

            if basis in ("qty", "quantity"):
                field = "qty"

            elif basis == "amount":
                field = "amount"

            elif basis == "cbm/weight":
                field = "custom_cbmweight"

            else:
                frappe.throw(
                    f"Unsupported allocation basis: {tax.custom_allocation_basis}"
                )

            total_basis = sum(
                flt(item.get(field)) for item in items
            )

            if total_basis <= 0:
                frappe.throw(
                    f"Total {tax.custom_allocation_basis} "
                    "must be greater than zero."
                )

            tax_allocated = 0

            for index, item in enumerate(items):

                basis_value = flt(item.get(field))

                if index == len(items) - 1:
                    # Assign rounding difference to last item
                    remaining = tax_amount - tax_allocated
                    allocated = remaining
                else:
                    allocated = flt(
                        tax_amount * basis_value / total_basis,
                        item.precision("applicable_charges")
                    )

                item.applicable_charges += allocated
                tax_allocated += allocated

            total_allocated += tax_allocated
