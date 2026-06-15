from app.parsers.txt_parser import TxtParser
from app.parsers.excel_reader import ExcelReader

from app.filters.column_filter import ColumnFilter
from app.filters.date_filter import DateFilter

from app.utils.file_detector import FileDetector
from app.utils.mac_utils import MacCleaner

from app.comparators.reconciliation_engine import ReconciliationEngine
from app.reports.excel_reporter import ExcelReporter


# ==================================================
# TXT FILE
# ==================================================

txt_file = FileDetector.get_latest_txt()

txt_df = TxtParser().parse(
    str(txt_file)
)

txt_df = MacCleaner.normalize(
    txt_df,
    "MAC Address"
)


# ==================================================
# INVENTORY EXCEL
# ==================================================

excel_file = FileDetector.get_latest_excel()

inventory_df = ExcelReader().read(
    str(excel_file)
)

inventory_df = ColumnFilter().extract(
    inventory_df
)

inventory_df = MacCleaner.normalize(
    inventory_df,
    "MAC Address"
)

inventory_df = DateFilter().filter_by_months(
    inventory_df,
    months=6
)


# ==================================================
# COMPARE
# ==================================================

engine = ReconciliationEngine()

matched, unmatched = engine.compare(
    txt_df,
    inventory_df
)


# ==================================================
# REPORTS
# ==================================================

reporter = ExcelReporter()

reporter.generate_reports(
    matched=matched,
    unmatched=unmatched,
    txt_count=txt_df.height
)


# ==================================================
# SUMMARY
# ==================================================

print("\n===================================")
print("NETWORK RECONCILIATION SUMMARY")
print("===================================")

print(f"TXT Records       : {txt_df.height}")
print(f"Inventory Records : {inventory_df.height}")
print(f"Matched Records   : {matched.height}")
print(f"Unmatched Records : {unmatched.height}")

print("\nReports Generated:")

print("output/reports/matched.xlsx")
print("output/reports/unmatched.xlsx")
print("output/reports/summary.xlsx")

print("\nPROCESS COMPLETED SUCCESSFULLY")