# Copyright (c) 2026, Milores and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CreditAgreement(Document):
	def on_submit(self):
		self.update_customer_credit_limit()

	def update_customer_credit_limit(self):
		if not self.customer_name or not self.company:
			return

		customer = frappe.get_doc("Customer", self.customer_name)

		credit_limit = frappe.utils.flt(
			self.equested_credit_equested_credit__limit_optional
		)
		credit_days = frappe.utils.cint(self.requested_credit_days)

		# Check if company already exists in Customer Credit Limits
		existing_row = None
		for row in customer.credit_limits:
			if row.company == self.company:
				existing_row = row
				break
		
		if existing_row:
		    existing_row.credit_limit = credit_limit
		    existing_row.custom_customer_credit_days_ = credit_days
		else:
			customer.append("credit_limits", {
				"company": self.company,
				"credit_limit": credit_limit,
				"custom_customer_credit_days_": credit_days,
				"bypass_credit_limit_check": 0
			})

		customer.save(ignore_permissions=True)
