frappe.ui.form.on('Sales Invoice', {
    refresh(frm) {
        // Fetch only for new documents
        if (frm.is_new() && frm.doc.company) {
            fetch_bank_account(frm);
        }
    },

    company(frm) {
        frm.set_value('custom_bank_account', '');

        if (frm.doc.company) {
            fetch_bank_account(frm);
        }
    }
});


async function fetch_bank_account(frm) {
    try {
        const accounts = await frappe.db.get_list('Bank Account', {
            filters: {
                company: frm.doc.company,
                disabled: 0
            },
            fields: ['name'],
            order_by: 'modified desc',
            limit: 1
        });

        const bank_account = accounts.length
            ? accounts[0].name
            : '';

        // Avoid unnecessary modification
        if (frm.doc.custom_bank_account !== bank_account) {
            await frm.set_value('custom_bank_account', bank_account);
        }

    } catch (error) {
        console.error('Error fetching Bank Account:', error);
    }
}