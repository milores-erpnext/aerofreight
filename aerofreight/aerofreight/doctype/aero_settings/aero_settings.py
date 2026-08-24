# Copyright (c) 2026, Milores and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AeroSettings(Document):
	def on_update(self):
		self.update_asset_account_managers()

	def update_asset_account_managers(self):
		for row in self.asset_manager_alignment:
			if not row.company or not row.user:
				continue

			user_data = frappe.db.get_value(
				"User",
				row.user,
				["enabled", "full_name"],
				as_dict=True
			)

			if not user_data:
				continue

			if not user_data.enabled:
				continue

			employees = frappe.get_all(
				"Employee",
				pluck="name"
			)

			if not employees:
				continue

			# Fetch current values too, not just names
			assets = frappe.get_all(
				"Asset",
				filters={
					"custodian": ["in", employees],
					"company": row.company
				},
				fields=[
					"name",
					"custom_custodian3_accounts_manager__",
					"custom_account_manager_name"
				]
			)

			for asset in assets:
				updates = {}

				if asset.custom_custodian3_accounts_manager__ != row.user:
					updates["custom_custodian3_accounts_manager__"] = row.user

				if asset.custom_account_manager_name != user_data.full_name:
					updates["custom_account_manager_name"] = user_data.full_name

				# Skip entirely if nothing changed
				if not updates:
					continue

				frappe.db.set_value(
					"Asset",
					asset.name,
					updates
				)