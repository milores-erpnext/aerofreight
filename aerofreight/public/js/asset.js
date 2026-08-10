frappe.ui.form.on("Asset", {
    setup: function (frm) {
        // Skip Frappe's automatic link validation for this field
        // (avoids the User.status permission error on validate_link_and_fetch)
        frm.set_df_property(
            "custom_custodian3_accounts_manager__",
            "ignore_link_validation",
            1
        );
    },

    custodian: async function (frm) {
        if (!frm.doc.custodian) {
            frm.set_value("custom_custodian3_accounts_manager__", "");
            frm.set_value("custom_account_manager_name", "");
            return;
        }

        const response = await frappe.call({
            method: "aerofreight.aerofreight.api.get_accounts_manager_for_custodian",
            args: {
                custodian: frm.doc.custodian
            }
        });

        const result = response.message || {};

        frm.set_value("custom_custodian3_accounts_manager__", result.user || "");
        frm.set_value("custom_account_manager_name", result.full_name || "");
    }
});