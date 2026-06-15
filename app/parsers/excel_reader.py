import polars as pl
from app.core.logger import get_logger

logger = get_logger()


class ExcelReader:

    def read(self, file_path: str) -> pl.DataFrame:

        logger.info(
            f"Reading Excel File: {file_path}"
        )

        df = pl.read_excel(
            file_path,
            engine="calamine"
        )

        logger.info(
            f"Rows Loaded: {df.height}"
        )

        logger.info(
            f"Columns: {df.columns}"
        )

        return df

#         https://chatgpt.com/g/g-p-6a2983bbba0481919e98baa621c3fd07/c/6a2aab6f-d2ac-83e8-ad40-faca3f500807


# https://chatgpt.com/share/6a2b77ad-7eb4-83e9-8bf5-a6e0d0afc247