const std_po = frappe.listview_settings["Purchase Order"] || {};

frappe.listview_settings["Purchase Order"] = Object.assign({}, std_po, {
	has_indicator_for_draft: true,

	add_fields: [
		...(std_po.add_fields || []),
		"status", "docstatus", "workflow_state", "per_received", "per_billed"
	],

	get_indicator(doc) {
		if (doc.docstatus === 2 || doc.status === "Cancelled") {
			return [__("Cancelled"), "red", "docstatus,=,2"];
		}

		// Ignore workflow_state, use real document status
		const status_colors = {
			"Draft": "red",
			"On Hold": "orange",
			"To Receive and Bill": "orange",
			"To Receive": "orange",
			"To Bill": "orange",
			"Delivered": "green",
			"Completed": "green",
			"Closed": "darkgrey"
		};

		const status = doc.status || "Draft";
		return [__(status), status_colors[status] || "gray", "status,=," + status];
	},
});
