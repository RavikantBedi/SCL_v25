import polars as pl
from app.core.logger import get_logger

logger = get_logger()


class ReconciliationEngine:
    """
    Compares TXT (network export) records against Excel inventory records.

    Matching strategy:
      - Primary: IP + MAC (both must match)
      - Falls back to MAC-only if IP column is missing from one side
    """

    def compare(
        self,
        txt_df: pl.DataFrame,
        inventory_df: pl.DataFrame,
    ):
        logger.info(
            f"Starting reconciliation | "
            f"TXT={txt_df.height} rows, "
            f"Inventory={inventory_df.height} rows"
        )

        # ====================================================
        # STANDARDISE TXT COLUMNS → IP, MAC
        # ====================================================
        txt_col_map = {
            "ip-address": "IP",
            "ip address":  "IP",
            "ipaddress":   "IP",
            "ip":          "IP",
            "IP Address":  "IP",
            "IP":          "IP",

            "mac-address": "MAC",
            "mac address": "MAC",
            "macaddress":  "MAC",
            "mac":         "MAC",
            "MAC Address": "MAC",
            "MAC":         "MAC",
        }

        txt_df = self._rename(txt_df, txt_col_map)
        logger.info(f"TXT columns after rename: {txt_df.columns}")

        # ====================================================
        # STANDARDISE INVENTORY COLUMNS → IP, MAC
        # ====================================================
        inv_col_map = {
            "IPAdd":        "IP",
            "ip address":   "IP",
            "ip addr":      "IP",
            "ipaddress":    "IP",
            "ip":           "IP",
            "IP Address":   "IP",
            "IP":           "IP",

            "MAC Address":  "MAC",
            "Mac Address":  "MAC",
            "mac address":  "MAC",
            "mac addr":     "MAC",
            "macaddress":   "MAC",
            "mac":          "MAC",
            "MAC":          "MAC",
        }

        inventory_df = self._rename(inventory_df, inv_col_map)
        logger.info(f"Inventory columns after rename: {inventory_df.columns}")

        # ====================================================
        # VALIDATE REQUIRED COLUMNS
        # ====================================================
        for col in ["IP", "MAC"]:
            if col not in txt_df.columns:
                raise ValueError(
                    f"TXT file is missing required column '{col}'. "
                    f"Columns found: {txt_df.columns}"
                )
            if col not in inventory_df.columns:
                raise ValueError(
                    f"Excel inventory is missing required column '{col}'. "
                    f"Columns found: {inventory_df.columns}"
                )

        # ====================================================
        # NORMALIZE — add clean key columns without dropping originals
        # ====================================================
        # MAC key: strip ALL non-hex characters (0-9, a-f only).
        # This handles every possible format:
        #   a464-a913-ed45  →  a464a913ed45
        #   A464A913ED45    →  a464a913ed45
        #   A4:64:A9:13:ED:45 → a464a913ed45
        # ====================================================

        # TXT: add normalized key columns _ip_key, _mac_key alongside originals
        txt_norm = txt_df.with_columns([
            pl.col("IP")
              .cast(pl.Utf8, strict=False)
              .fill_null("")
              .str.strip_chars()
              .alias("_ip_key"),

            pl.col("MAC")
              .cast(pl.Utf8, strict=False)
              .fill_null("")
              .str.to_lowercase()
              .str.replace_all(r"[^0-9a-f]", "")   # keep ONLY hex digits
              .alias("_mac_key"),
        ])

        # Inventory: add normalized key columns _ip_key, _mac_key alongside originals
        inv_norm = inventory_df.with_columns([
            pl.col("IP")
              .cast(pl.Utf8, strict=False)
              .fill_null("")
              .str.strip_chars()
              .alias("_ip_key"),

            pl.col("MAC")
              .cast(pl.Utf8, strict=False)
              .fill_null("")
              .str.to_lowercase()
              .str.replace_all(r"[^0-9a-f]", "")   # keep ONLY hex digits
              .alias("_mac_key"),
        ])

        logger.info(f"TXT sample (normalized keys):\n{txt_norm.select(['IP','MAC','_ip_key','_mac_key']).head(5)}")
        logger.info(f"Inventory sample (normalized keys):\n{inv_norm.select(['IP','MAC','_ip_key','_mac_key']).head(5)}")

        # Drop the renamed IP/MAC columns from inventory before join to avoid
        # duplicate column names; keep only extra inventory columns + keys
        inv_keys_only = inv_norm.drop(["IP", "MAC"])

        # ====================================================
        # MATCH on IP + MAC keys
        # TXT rows whose (IP+MAC) pair exists in inventory,
        # with full inventory data joined in.
        # ====================================================
        matched = txt_norm.join(
            inv_keys_only,
            left_on=["_ip_key", "_mac_key"],
            right_on=["_ip_key", "_mac_key"],
            how="inner"
        ).drop(["_ip_key", "_mac_key"])

        # ====================================================
        # UNMATCHED = TXT rows with no inventory match + INVENTORY rows with no TXT match
        # ====================================================
        txt_unmatched_raw = txt_norm.join(
            inv_keys_only.select(["_ip_key", "_mac_key"]),
            left_on=["_ip_key", "_mac_key"],
            right_on=["_ip_key", "_mac_key"],
            how="anti"
        )

        # Best-effort fill: for unmatched TXT records, try to populate missing inventory 
        # fields (like CompName, Last AgentCom) by looking up the MAC address in the inventory.
        inv_lookup_by_mac = (
            inv_keys_only
            .drop("_ip_key")
            .filter(pl.col("_mac_key") != "")
            .unique(subset=["_mac_key"], keep="first")
        )

        txt_unmatched = txt_unmatched_raw.join(
            inv_lookup_by_mac,
            left_on="_mac_key",
            right_on="_mac_key",
            how="left"
        ).drop(["_ip_key", "_mac_key"])

        inv_unmatched = inv_norm.join(
            txt_norm.select(["_ip_key", "_mac_key"]),
            left_on=["_ip_key", "_mac_key"],
            right_on=["_ip_key", "_mac_key"],
            how="anti"
        ).drop(["_ip_key", "_mac_key"])

        unmatched = pl.concat([txt_unmatched, inv_unmatched], how="diagonal")

        logger.info(
            f"Reconciliation done | "
            f"Matched={matched.height}, "
            f"Unmatched={unmatched.height}"
        )

        return matched, unmatched

    # ──────────────────────────────────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def _rename(df: pl.DataFrame, col_map: dict) -> pl.DataFrame:
        """Case-insensitive rename using the provided mapping."""
        rename = {}
        for col in df.columns:
            # Try exact match first, then lower-stripped
            if col in col_map:
                rename[col] = col_map[col]
            elif col.strip().lower() in {k.lower(): v for k, v in col_map.items()}:
                lower_map = {k.lower(): v for k, v in col_map.items()}
                rename[col] = lower_map[col.strip().lower()]
        return df.rename(rename) if rename else df

    @staticmethod
    def _normalize(df: pl.DataFrame) -> pl.DataFrame:
        """Normalise IP and MAC so minor formatting differences don't block matching."""
        return df.with_columns([
            # IP: strip whitespace
            pl.col("IP")
              .cast(pl.Utf8, strict=False)
              .fill_null("")
              .str.strip_chars(),

            # MAC: lowercase, remove separators (: - . spaces)
            pl.col("MAC")
              .cast(pl.Utf8, strict=False)
              .fill_null("")
              .str.to_lowercase()
              .str.replace_all(r"[-:\.\s]", ""),
        ])