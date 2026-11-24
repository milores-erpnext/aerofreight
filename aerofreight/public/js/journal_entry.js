frappe.ui.form.on('Journal Entry', {
    refresh(frm) {
        if (!frm.doc.custom_barcode) {
            frm.set_value('custom_barcode', frm.doc.name);
        }
    }
});
