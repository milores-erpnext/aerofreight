frappe.ui.form.on("Landed Cost Voucher", {
    refresh(frm) {
        frm.set_df_property("distribute_charges_based_on", "hidden", 1);
        set_cbmweight_properties(frm);
    }
});

frappe.ui.form.on("Landed Cost Taxes and Charges", {
    custom_allocation_basis(frm, cdt, cdn) {
        set_cbmweight_properties(frm);
    }
});

function set_cbmweight_properties(frm) {
    let is_cbm_weight = (frm.doc.taxes || []).some(
        row => row.custom_allocation_basis === "CBM/Weight"
    );

    frm.fields_dict.items.grid.update_docfield_property(
        "custom_cbmweight",
        "read_only",
        is_cbm_weight ? 0 : 1
    );

    frm.fields_dict.items.grid.update_docfield_property(
        "custom_cbmweight",
        "reqd",
        is_cbm_weight ? 1 : 0
    );

    frm.refresh_field("items");
}
