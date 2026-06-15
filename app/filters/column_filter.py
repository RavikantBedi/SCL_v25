import polars as pl


class ColumnFilter:

    COLUMN_MAPPING = {
        # IP
        "IPAdd": "IPAdd",
        "IP address": "IPAdd",
        "IPAddress": "IPAdd",

        # MAC
        "MAC Address": "MAC Address",

        # Computer Name
        "CompName": "CompName",
        "Computer Name": "CompName",

        # User
        "User Name": "User Name",

        # Model
        "System Model": "System Model",

        # Last Agent
        "Last AgentCom": "Last AgentCom",
        "Last Agent Comm": "Last AgentCom",
    }

    REQUIRED_COLUMNS = [
        "IPAdd",
        "MAC Address",
        "CompName",
        "User Name",
        "System Model",
        "Last AgentCom"
    ]

    def extract(
        self,
        df: pl.DataFrame
    ) -> pl.DataFrame:

        rename_map = {}

        for col in df.columns:

            if col in self.COLUMN_MAPPING:

                rename_map[col] = (
                    self.COLUMN_MAPPING[col]
                )

        df = df.rename(rename_map)

        available = [
            col
            for col in self.REQUIRED_COLUMNS
            if col in df.columns
        ]

        return df.select(available)