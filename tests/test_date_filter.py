from app.parsers.excel_reader import ExcelReader
from app.filters.column_filter import ColumnFilter
from app.filters.date_filter import DateFilter

from app.utils.file_detector import FileDetector
from app.utils.mac_utils import MacCleaner   # <-- ADD THIS


excel_file = FileDetector.get_latest_excel()

reader = ExcelReader()

df = reader.read(
    str(excel_file)
)

filtered = ColumnFilter().extract(
    df
)

# Normalize MAC Address
filtered = MacCleaner.normalize(
    filtered,
    "MAC Address"
)

print("\nBefore Filter:")
print(filtered.height)

date_filter = DateFilter()

result = date_filter.filter_by_months(
    filtered,
    months=3
)

print("\nAfter Filter:")
print(result.height)

print("\nSample Data:\n")
print(result.head())