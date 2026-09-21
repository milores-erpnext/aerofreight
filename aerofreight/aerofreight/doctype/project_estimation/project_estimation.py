# Copyright (c) 2026, Milores and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ProjectEstimation(Document):
	def validate(self):
		self.calculate_profit()
		self.set("boq_summary", [])
		
		rows = [
			{"description": "Income", "income": self.get("4")},
			{"description": "Material Charges","expenses": self.total_items},
			{"description": "Freight Charges","expenses": self.total_freight},
			{"description": "Local Charges","expenses": self.total_local_charges},
			{"description": "Site Charges","expenses": self.total_site_charges},
			{"description": "Manpower Charges","expenses": self.total_manpower},
			{"description": "Total","income": self.get("4"),"expenses": self.get("8"),"profit": self.get("14"),"_of_profit": self.profit_percent},
		]
		
		for row in rows:
			self.append("boq_summary", row)

	def calculate_profit(self):
		total_income = frappe.utils.flt(self.get("4"))
		total_expense = frappe.utils.flt(self.get("8"))

		self.set("14", total_income - total_expense)

		if total_income:
			self.profit_percent = (self.get("14") / total_expense) * 100
		else:
			self.profit_percent = 0

	def on_submit(self):
		frappe.db.set_value("Project", self.project, "estimated_costing", self.get("8"))
