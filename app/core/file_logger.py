from pathlib import Path
from datetime import datetime


class FileLogger:

    LOG_DIR = Path("logs")

    @classmethod
    def log(cls, filename, message):

        cls.LOG_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        log_file = cls.LOG_DIR / filename

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        with open(
            log_file,
            "a",
            encoding="utf-8"
        ) as f:

            f.write(
                f"[{timestamp}] {message}\n"
            )

    @classmethod
    def info(cls, message):

        cls.log(
            "application.log",
            f"INFO: {message}"
        )

    @classmethod
    def error(cls, message):

        cls.log(
            "error.log",
            f"ERROR: {message}"
        )

    @classmethod
    def process(cls, message):

        cls.log(
            "processing.log",
            message
        )