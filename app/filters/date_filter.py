from datetime import datetime, timedelta
import polars as pl


class DateFilter:

    DATE_COLUMN_CANDIDATES = [
        "Last AgentCom",
        "Last Agent Comm",
        "LastAgentCom",
    ]

    def filter_by_months(
        self,
        df: pl.DataFrame,
        months: int = 6
    ) -> pl.DataFrame:

        date_column = None

        for col in self.DATE_COLUMN_CANDIDATES:
            if col in df.columns:
                date_column = col
                break

        if date_column is None:
            print(
                "\n[WARNING] Date column not found."
                "\nSkipping date filtering."
            )
            return df

        cutoff_date = (
            datetime.now()
            - timedelta(days=months * 30)
        )

        print(
            f"\nApplying Date Filter:"
            f"\nColumn: {date_column}"
            f"\nMonths: {months}"
            f"\nCutoff: {cutoff_date}"
        )

        try:

            # Support:
            # 27/01/26 09:21:37 IST
            # 27/01/26 09:21:37
            # 2026-01-27 09:21:37

            df = df.with_columns(
                pl.col(date_column)
                .cast(pl.Utf8)
                .str.replace(" IST", "")
                .str.strptime(
                    pl.Datetime,
                    "%d/%m/%y %H:%M:%S",
                    strict=False
                )
                .alias(date_column)
            )

            filtered_df = df.filter(
                pl.col(date_column) >= cutoff_date
            )

            print(
                f"\nRows Before Filter : {df.height}"
                f"\nRows After Filter  : {filtered_df.height}"
            )

            return filtered_df

        except Exception as e:

            print(
                f"\n[WARNING] Date parsing failed:"
                f"\n{e}"
                f"\nSkipping date filter."
            )

            return df