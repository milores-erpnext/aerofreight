// Copyright (c) 2026, Milores and contributors
// For license information, please see license.txt

frappe.ui.form.on("Project Estimation", {
    setup(frm) {
        frm.set_query("project", function () {
            return {
                filters: {
                    company: frm.doc.company
                }
            };
        });
    },

    company(frm) {
        frm.set_value("project", "");
    }
});
