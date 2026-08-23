Dear {{ doc.applicant_name }},

Congratulations!

We are pleased to inform you that your application for the position of **{{ doc.designation or doc.job_title }}** has been **accepted**.
We appreciate your interest in joining our organization and are excited to move forward with you in the hiring process.
Our HR team will contact you shortly with the next steps, including any required documentation, interview scheduling, or onboarding details.
If you have any questions, please feel free to contact us.

We look forward to welcoming you to our team.

Best Regards,
**{{ frappe.db.get_single_value("Global Defaults", "default_company") or "HR Team" }}**