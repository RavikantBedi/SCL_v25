from pathlib import Path


class FileDetector:

    @staticmethod
    def get_latest_excel():

        excel_folder = Path("input/excel")

        files = list(
            excel_folder.glob("*.xlsx")
        )

        if not files:
            raise FileNotFoundError(
                "No Excel file found in input/excel"
            )

        return max(
            files,
            key=lambda x: x.stat().st_mtime
        )

    @staticmethod
    def get_latest_txt():

        txt_folder = Path("input/txt")

        files = list(
            txt_folder.glob("*.txt")
        )

        if not files:
            raise FileNotFoundError(
                "No TXT file found in input/txt"
            )

        return max(
            files,
            key=lambda x: x.stat().st_mtime
        )