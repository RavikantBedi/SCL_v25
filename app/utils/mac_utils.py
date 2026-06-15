import polars as pl


class MacCleaner:

    @staticmethod
    def normalize(df, column):

        return df.with_columns(
            pl.col(column)
            .cast(pl.Utf8)
            .str.to_lowercase()
            .str.replace_all("-", "")
            .str.replace_all(":", "")
            .str.replace_all(".", "", literal=True)
            .str.replace_all(" ", "")
            .alias(column)
        )