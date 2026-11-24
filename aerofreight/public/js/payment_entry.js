frappe.ui.form.on('Payment Entry', {
    refresh(frm) {
        if (!frm.doc.custom_barcode) {
            frm.set_value('custom_barcode', frm.doc.name);
        }
    }
});
