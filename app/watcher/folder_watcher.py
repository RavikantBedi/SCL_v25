from pathlib import Path
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler

import threading
import time

from app.parsers.txt_parser import TxtParser
from app.parsers.excel_reader import ExcelReader

from app.filters.column_filter import ColumnFilter
from app.filters.date_filter import DateFilter

from app.utils.mac_utils import MacCleaner
from app.utils.archive_manager import ArchiveManager

from app.comparators.reconciliation_engine import ReconciliationEngine
from app.reports.excel_reporter import ExcelReporter

from app.core.file_logger import FileLogger


WATCH_FOLDER = Path("input/incoming")

PROCESS_DELAY = 5

processing_timer = None
processing_lock = threading.Lock()


def wait_for_file(file_path, retries=10):

    for _ in range(retries):

        try:

            with open(file_path, "rb"):
                return True

        except PermissionError:

            time.sleep(1)

        except FileNotFoundError:

            return False

    return False


def safe_process():

    if processing_lock.locked():
        return

    with processing_lock:

        txt_files = list(
            WATCH_FOLDER.glob("*.txt")
        )

        excel_files = (
            list(WATCH_FOLDER.glob("*.xlsx"))
            +
            list(WATCH_FOLDER.glob("*.xls"))
        )

        if not txt_files:
            return

        if not excel_files:
            return

        try:

            print(
                "\nWaiting for files to stabilize..."
            )

            FileLogger.info(
                "File processing started"
            )

            process_files()

        except Exception as e:

            FileLogger.error(
                str(e)
            )

            print(
                f"\nPROCESSING ERROR: {e}"
            )


class ReconciliationHandler(FileSystemEventHandler):

    def on_created(self, event):

        global processing_timer

        if event.is_directory:
            return

        print(
            f"\nFile Event: {event.src_path}"
        )

        FileLogger.info(
            f"File detected: {event.src_path}"
        )

        if processing_timer:
            processing_timer.cancel()

        processing_timer = threading.Timer(
            PROCESS_DELAY,
            safe_process
        )

        processing_timer.start()


def process_files():

    txt_files = list(
        WATCH_FOLDER.glob("*.txt")
    )

    excel_files = (
        list(WATCH_FOLDER.glob("*.xlsx"))
        +
        list(WATCH_FOLDER.glob("*.xls"))
    )

    if not txt_files or not excel_files:

        print(
            "\nWaiting for both TXT and Excel files..."
        )

        FileLogger.info(
            "Waiting for TXT and Excel files"
        )

        return

    txt_file = txt_files[0]
    excel_file = excel_files[0]

    if not txt_file.exists():
        return

    if not excel_file.exists():
        return

    if not wait_for_file(txt_file):

        msg = f"Cannot access TXT file: {txt_file}"

        print(f"\n{msg}")

        FileLogger.error(msg)

        return

    if not wait_for_file(excel_file):

        msg = f"Cannot access Excel file: {excel_file}"

        print(f"\n{msg}")

        FileLogger.error(msg)

        return

    print("\n=================================")
    print("PROCESSING FILES")
    print("=================================")

    print(f"TXT   : {txt_file.name}")
    print(f"Excel : {excel_file.name}")

    FileLogger.process(
        f"TXT={txt_file.name}, EXCEL={excel_file.name}"
    )

    # ---------------- TXT ----------------

    txt_df = TxtParser().parse(
        str(txt_file)
    )

    txt_df = MacCleaner.normalize(
        txt_df,
        "MAC Address"
    )

    # ---------------- EXCEL ----------------

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

    # ---------------- COMPARE ----------------

    matched, unmatched = (
        ReconciliationEngine().compare(
            txt_df,
            inventory_df
        )
    )

    # ---------------- REPORT ----------------

    ExcelReporter().generate_reports(
        matched=matched,
        unmatched=unmatched,
        txt_count=txt_df.height
    )

    # ---------------- ARCHIVE ----------------

    ArchiveManager.archive_files(
        txt_file,
        excel_file
    )

    print("\n=================================")
    print("PROCESS COMPLETED SUCCESSFULLY")
    print("=================================")

    print(f"TXT Records       : {txt_df.height}")
    print(f"Inventory Records : {inventory_df.height}")
    print(f"Matched Records   : {matched.height}")
    print(f"Unmatched Records : {unmatched.height}")

    FileLogger.process(
        f"Matched={matched.height}, Unmatched={unmatched.height}"
    )

    FileLogger.info(
        "Processing completed successfully"
    )

    print("\nReports Generated:")
    print("output/reports/matched.xlsx")
    print("output/reports/unmatched.xlsx")
    print("output/reports/summary.xlsx")


if __name__ == "__main__":

    WATCH_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    observer = Observer()

    observer.schedule(
        ReconciliationHandler(),
        str(WATCH_FOLDER),
        recursive=False
    )

    observer.start()

    print(
        f"\nWatching Folder: {WATCH_FOLDER.resolve()}"
    )

    # Process existing files at startup
    safe_process()

    FileLogger.info(
        "Folder watcher started"
    )

    try:

        while True:
            time.sleep(1)

    except KeyboardInterrupt:

        observer.stop()

        FileLogger.info(
            "Folder watcher stopped"
        )

    observer.join()