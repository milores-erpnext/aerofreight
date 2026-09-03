__version__ = "0.0.1"
import erpnext.accounts.report.customer_ledger_summary.customer_ledger_summary as core_report
from aerofreight.aerofreight.overrides.customer_ledger_summary import execute as custom_execute

core_report.execute = custom_execute