Object.defineProperty(frappe.query_reports, "Customer Ledger Summary", {
    configurable: true,
    enumerable: true,

    set(report_settings) {
        // Add filter only once
        if (!report_settings.filters.some(f => f.fieldname === "range")) {
            report_settings.filters.push({
                fieldname: "range",
                label: __("Ageing Range"),
                fieldtype: "Data",
                default: "30,60,90,120",
            });
        }

        this._patched_report_settings = report_settings;
    },

    get() {
        return this._patched_report_settings;
    }
});
