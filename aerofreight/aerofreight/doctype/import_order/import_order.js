// Copyright (c) 2026, Milores and contributors
// For license information, please see license.txt

frappe.ui.form.on("Import Order", {
    refresh: function (frm) {
        frm.add_custom_button(__("Attach XML"), function () {
            open_xml_upload_dialog(frm);
        });
    },
});

function open_xml_upload_dialog(frm) {
    const dialog = new frappe.ui.Dialog({
        title: __("Attach XML"),
        fields: [
            {
                fieldname: "xml_html",
                fieldtype: "HTML",
                options: `
                    <div>
                        <input type="file" id="xml_file_input" accept=".xml,text/xml" />
                        <p class="text-muted small" style="margin-top:8px;">
                            ${__("Select an .xml file.")}
                        </p>
                    </div>
                `,
            },
        ],
        primary_action_label: __("Import"),
        primary_action: function () {
            const input = dialog.$wrapper.find("#xml_file_input")[0];
            const file = input && input.files && input.files[0];

            if (!file) {
                frappe.msgprint(__("Please choose an XML file first."));
                return;
            }

            const reader = new FileReader();
            reader.onload = function (e) {
                parse_and_set_fields(frm, e.target.result);
                dialog.hide();
            };
            reader.onerror = function () {
                frappe.msgprint({
                    title: __("Error"),
                    message: __("Could not read the selected file."),
                    indicator: "red",
                });
            };
            reader.readAsText(file);
        },
    });

    dialog.show();
}

// ---------- helpers ----------

function normalize(str) {
    return (str || "")
        .toString()
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, ""); // strip spaces, underscores, punctuation
}

function words_of(str) {
    return (str || "")
        .toString()
        .toLowerCase()
        .split(/[^a-z0-9]+/)
        .filter((w) => w.length > 2); // ignore tiny/noise words
}

// Returns true if tag_key fuzzily matches a form field's fieldname or label
function is_fuzzy_match(tag_norm, tag_words, field_norm, field_words) {
    if (!tag_norm || !field_norm) return false;

    // 1. exact normalized match
    if (tag_norm === field_norm) return true;

    // 2. one contains the other (substring)
    if (tag_norm.length >= 3 && field_norm.length >= 3) {
        if (tag_norm.includes(field_norm) || field_norm.includes(tag_norm)) {
            return true;
        }
    }

    // 3. shared significant word
    for (const w of tag_words) {
        if (field_words.includes(w)) return true;
    }

    return false;
}

// ---------- main ----------

function parse_and_set_fields(frm, xml_text) {
    console.log("=== Attach XML: raw file content ===");
    console.log(xml_text);

    let xml_doc;
    try {
        const parser = new DOMParser();
        xml_doc = parser.parseFromString(xml_text, "application/xml");

        const parse_error = xml_doc.getElementsByTagName("parsererror");
        if (parse_error.length) {
            throw new Error("Invalid XML");
        }
    } catch (e) {
        frappe.msgprint({
            title: __("Error"),
            message: __("The selected file is not valid XML."),
            indicator: "red",
        });
        return;
    }

    // Collect raw tag/attribute -> value pairs from the XML (any shape)
    const raw_found = {}; // { rawKey: value }
    const all_elements = xml_doc.getElementsByTagName("*");

    for (let i = 0; i < all_elements.length; i++) {
        const el = all_elements[i];

        // Shape 1: leaf tag, e.g. <vessel>q</vessel> / <VesselName>q</VesselName>
        if (el.children.length === 0) {
            const text_val = el.textContent ? el.textContent.trim() : "";
            if (text_val !== "") {
                raw_found[el.tagName] = text_val;
            }
        }

        // Shape 2: <field name="Vessel">q</field> / fieldname=/value= attrs
        const attr_name =
            el.getAttribute("name") ||
            el.getAttribute("fieldname") ||
            el.getAttribute("field") ||
            el.getAttribute("label");
        if (attr_name) {
            const attr_val =
                el.getAttribute("value") !== null
                    ? el.getAttribute("value")
                    : el.textContent
                    ? el.textContent.trim()
                    : "";
            if (attr_val !== "") {
                raw_found[attr_name] = attr_val;
            }
        }

        // Shape 3: attributes directly on any element, e.g. <doc vessel="q" .../>
        if (el.attributes && el.attributes.length) {
            for (let a = 0; a < el.attributes.length; a++) {
                const attr = el.attributes[a];
                const akey = attr.name.toLowerCase();
                if (
                    akey !== "name" &&
                    akey !== "fieldname" &&
                    akey !== "field" &&
                    akey !== "label" &&
                    akey !== "value" &&
                    attr.value !== ""
                ) {
                    raw_found[attr.name] = attr.value;
                }
            }
        }
    }

    console.log("=== Attach XML: raw tag/attribute values detected ===", raw_found);

    // Build a list of this form's fields with normalized fieldname + label
    const field_list = Object.keys(frm.fields_dict)
        .map((fieldname) => {
            const df = frm.fields_dict[fieldname].df || {};
            return {
                fieldname,
                fieldname_norm: normalize(fieldname),
                fieldname_words: words_of(fieldname),
                label_norm: normalize(df.label || ""),
                label_words: words_of(df.label || ""),
            };
        })
        // skip layout-only fields
        .filter((f) => !["Tab Break", "Section Break", "Column Break"].includes(
            (frm.fields_dict[f.fieldname].df || {}).fieldtype
        ));

    // Fuzzy-match every raw tag/attribute against the field list
    let updated_count = 0;
    let updated_fields = [];
    let skipped_unmatched = [];
    const already_set = {};

    Object.keys(raw_found).forEach((raw_key) => {
        const value = raw_found[raw_key];
        const tag_norm = normalize(raw_key);
        const tag_words = words_of(raw_key);

        let match = null;
        for (const f of field_list) {
            if (already_set[f.fieldname]) continue; // don't overwrite once set
            if (
                is_fuzzy_match(tag_norm, tag_words, f.fieldname_norm, f.fieldname_words) ||
                is_fuzzy_match(tag_norm, tag_words, f.label_norm, f.label_words)
            ) {
                match = f;
                break;
            }
        }

        if (match) {
            frm.set_value(match.fieldname, value);
            already_set[match.fieldname] = true;
            updated_count++;
            updated_fields.push(`${raw_key} -> ${match.fieldname}`);
        } else {
            skipped_unmatched.push(raw_key);
        }
    });

    frm.refresh_fields();

    console.log("=== Attach XML: fuzzy matches applied ===", updated_fields);
    console.log("=== Attach XML: tags with no fuzzy match ===", skipped_unmatched);

    if (updated_count) {
        frappe.show_alert({
            message: __("{0} field(s) updated from XML.", [updated_count]),
            indicator: "green",
        });
    } else {
        frappe.msgprint({
            title: __("No Matching Fields"),
            message: __(
                "Still no fuzzy matches. Open the browser console (F12) — 'raw tag/attribute values detected' shows exactly what was found in your file."
            ),
            indicator: "orange",
        });
    }
}