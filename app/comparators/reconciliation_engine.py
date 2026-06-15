import polars as pl


class ReconciliationEngine:

    def compare(
        self,
        txt_df: pl.DataFrame,
        inventory_df: pl.DataFrame
    ):

        # =====================================
        # TXT COLUMN STANDARDIZATION
        # =====================================

        txt_mapping = {
            "ip-address": "IP",
            "IP Address": "IP",
            "ip address": "IP",
            "IP": "IP",

            "mac-address": "MAC",
            "MAC Address": "MAC",
            "mac address": "MAC",
            "MAC": "MAC"
        }

        txt_rename = {}

        for old_col in txt_df.columns:
            if old_col in txt_mapping:
                txt_rename[old_col] = txt_mapping[old_col]

        txt_df = txt_df.rename(txt_rename)

        # =====================================
        # EXCEL COLUMN STANDARDIZATION
        # =====================================

        excel_mapping = {
            "IPAdd": "IP",
            "IP Address": "IP",
            "IP address": "IP",
            "IPAddress": "IP",
            "IP": "IP",

            "MAC Address": "MAC",
            "Mac Address": "MAC",
            "MAC": "MAC"
        }

        excel_rename = {}

        for old_col in inventory_df.columns:
            if old_col in excel_mapping:
                excel_rename[old_col] = excel_mapping[old_col]

        inventory_df = inventory_df.rename(
            excel_rename
        )

        # =====================================
        # VALIDATION
        # =====================================

        required = ["IP", "MAC"]

        for col in required:

            if col not in txt_df.columns:
                raise ValueError(
                    f"TXT missing column '{col}'. "
                    f"Available: {txt_df.columns}"
                )

            if col not in inventory_df.columns:
                raise ValueError(
                    f"Excel missing column '{col}'. "
                    f"Available: {inventory_df.columns}"
                )

        # =====================================
        # KEEP REQUIRED COLUMNS
        # =====================================

        txt_compare = txt_df.select(
            ["IP", "MAC"]
        )

        inventory_compare = inventory_df.select(
            ["IP", "MAC"]
        )

        # =====================================
        # NORMALIZE VALUES
        # =====================================

        txt_compare = txt_compare.with_columns([
            pl.col("IP")
            .cast(pl.Utf8)
            .str.strip_chars(),

            pl.col("MAC")
            .cast(pl.Utf8)
            .str.to_lowercase()
            .str.replace_all("-", "")
            .str.replace_all(":", "")
            .str.replace_all(".", "", literal=True)
            .str.replace_all(" ", "")
        ])

        inventory_compare = inventory_compare.with_columns([
            pl.col("IP")
            .cast(pl.Utf8)
            .str.strip_chars(),

            pl.col("MAC")
            .cast(pl.Utf8)
            .str.to_lowercase()
            .str.replace_all("-", "")
            .str.replace_all(":", "")
            .str.replace_all(".", "", literal=True)
            .str.replace_all(" ", "")
        ])

        # =====================================
        # DEBUG
        # =====================================

        print("\nTXT FOR COMPARISON")
        print(txt_compare)

        print("\nINVENTORY FOR COMPARISON")
        print(inventory_compare)

        # =====================================
        # MATCHED
        # =====================================

        matched = txt_compare.join(
            inventory_compare,
            on=["IP", "MAC"],
            how="inner"
        )

        # =====================================
        # UNMATCHED
        # =====================================

        unmatched = txt_compare.join(
            inventory_compare,
            on=["IP", "MAC"],
            how="anti"
        )

        return matched, unmatched