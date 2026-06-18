import polars as pl
from datetime import datetime, timedelta
from pathlib import Path
import random

system_models = [
    "HP Z200 Workstation",
    "Dell OptiPlex 7080",
    "Dell Precision 3640",
    "Lenovo ThinkCentre M720",
    "HP EliteDesk 800",
    "HP ProDesk 600",
]

domains = [
    "FABNET",
    "CORPNET",
    "OFFICE",
]

users = [
    "ravi",
    "amit",
    "priya",
    "rahul",
    "sunanya",
    "dharamveer",
    "admin",
    "guest",
]

rows = []

for i in range(1, 101):

    # First 3 rows will match TXT file
    if i == 1:
        ip = "10.193.10.25"
        mac = "40ab-f061-b991"

    elif i == 2:
        ip = "10.193.10.26"
        mac = "5065-f8aa-bbcc"

    elif i == 3:
        ip = "10.193.10.27"
        mac = "7c10-c9aa-bb01"

    else:
        ip = f"10.193.{random.randint(1,50)}.{random.randint(1,254)}"

        mac = (
            f"{random.randint(0,65535):04x}-"
            f"{random.randint(0,65535):04x}-"
            f"{random.randint(0,65535):04x}"
        )

    # Random dates from last 12 months
    random_days = random.randint(1, 365)

    rows.append(
        {
            "SR": i,
            "IPAdd": ip,
            "CompName": f"PC-{i:03}",
            "DomainName": random.choice(domains),
            "ESTPVer": f"10.{random.randint(1,9)}.0",
            "ESTPDATVer": str(random.randint(5000,7000)),
            "AgentVER": f"{random.randint(1,5)}.{random.randint(0,9)}",
            "DLPEVer": f"{random.randint(1,5)}.{random.randint(0,9)}",
            "Last AgentCom": (
                datetime.now()
                - timedelta(days=random_days)
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "User Name": random.choice(users),
            "MAC Address": mac,
            "System Model": random.choice(system_models),
        }
    )

df = pl.DataFrame(rows)

Path("input/excel").mkdir(
    parents=True,
    exist_ok=True
)

output_file = "input/excel/inventory_test.xlsx"

df.write_excel(output_file)

print(f"Created: {output_file}")
print(f"Rows: {df.height}")