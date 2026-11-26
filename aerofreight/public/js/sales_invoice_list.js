frappe.listview_settings["Sales Invoice"] = {
    onload(listview) {
        listview.page.add_actions_menu_item(__("Print GTA"), () => {
            const names = listview.get_checked_items(true);
            if (!names.length) return frappe.msgprint(__("Select invoices first"));
            const url = "/api/method/aerofreight.aerofreight.api.download_invoices_zip?names=" +
                encodeURIComponent(JSON.stringify(names)) +
                "&print_format=Standard";
            window.open(url);
        });
    }
};
