from pathlib import Path
import shutil


class ArchiveManager:

    TXT_ARCHIVE = Path("archive/txt")
    EXCEL_ARCHIVE = Path("archive/excel")

    @classmethod
    def archive_files(
        cls,
        txt_file,
        excel_file
    ):

        cls.TXT_ARCHIVE.mkdir(
            parents=True,
            exist_ok=True
        )

        cls.EXCEL_ARCHIVE.mkdir(
            parents=True,
            exist_ok=True
        )

        txt_destination = (
            cls.TXT_ARCHIVE /
            txt_file.name
        )

        excel_destination = (
            cls.EXCEL_ARCHIVE /
            excel_file.name
        )

        try:

            # TXT FILE
            if txt_file.exists():

                if txt_destination.exists():
                    txt_destination.unlink()

                shutil.move(
                    str(txt_file),
                    str(txt_destination)
                )

            # EXCEL FILE
            if excel_file.exists():

                if excel_destination.exists():
                    excel_destination.unlink()

                shutil.move(
                    str(excel_file),
                    str(excel_destination)
                )

            print(
                "\nFiles Archived Successfully"
            )

            print(
                f"TXT   -> {txt_destination}"
            )

            print(
                f"Excel -> {excel_destination}"
            )

        except Exception as e:

            print(
                f"\nArchive Error: {e}"
            )