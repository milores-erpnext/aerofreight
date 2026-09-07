frappe.ui.form.on("Opportunity", {
    custom_reschedule_button(frm) {
        if (!frm.doc.custom_reschedule) {
            frappe.msgprint(__("Please select a Reschedule Date first."));
            return;
        }
        frm.save()
        frappe.call({
            method: "aerofreight.aerofreight.api.reschedule_opportunity",
            args: {
                opportunity_name: frm.doc.name,
            },
            freeze: true,
            freeze_message: __("Creating Rescheduled Opportunity..."),
            callback(r) {
                if (r.message) {
                    frappe.show_alert({
                        message: __("Rescheduled Opportunity Created: {0}", [r.message]),
                        indicator: "green",
                    });

                    // Reload current document to update reschedule flag
                    frm.reload_doc();

                    // Optional: Open the newly created Opportunity
                    // frappe.set_route("Form", "Opportunity", r.message);
                }
            },
        });
    },
});