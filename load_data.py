"""Read PhonePe JSON files and save their values in nine SQL tables."""

import argparse
import json
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "data" / "phonepe.db"
# This preserved fork has the legacy fields required by the project PDF.
SOURCE_URL = "https://github.com/sunil-chaudhary-phonepe-com/pulse.git"
SOURCE_COMMIT = "bf862f22ce42949a183bf65a9b8aa50110101199"


def read_files(folder):
    """Yield state, year, quarter and JSON data, one file at a time."""
    for file in sorted(folder.rglob("*.json")):
        parts = file.relative_to(folder).parts
        # National file: 2024/1.json. State file: state/tamil-nadu/2024/1.json.
        state = parts[1] if parts[0] == "state" else "india"
        year = int(file.parent.name)
        quarter = int(file.stem)
        with file.open(encoding="utf-8") as stream:
            data = json.load(stream)["data"]
        yield state, year, quarter, data


def insert_rows(connection, table, rows):
    if rows:
        placeholders = ",".join(["?"] * len(rows[0]))
        connection.executemany(f"INSERT INTO {table} VALUES ({placeholders})", rows)


def load_aggregated(connection, root, kind, table):
    rows = []
    folder = root / "data" / "aggregated" / kind / "country" / "india"
    for state, year, quarter, data in read_files(folder):
        if state == "india":
            continue  # National and state totals would double count the same activity.
        if kind == "user":
            values = data["aggregated"]
            rows.append((state, year, quarter,
                         values.get("registeredUsers", values.get("registeredCount")),
                         values.get("appOpens")))
        else:
            for category in data.get("transactionData", []):
                metric = category["paymentInstruments"][0]
                rows.append((state, year, quarter, category["name"],
                             metric["count"], metric.get("amount")))
    insert_rows(connection, table, rows)


def load_map(connection, root, kind, table):
    rows = []
    folder = root / "data" / "map" / kind / "hover" / "country" / "india"
    for state, year, quarter, data in read_files(folder):
        if state == "india":
            continue
        if kind == "user":
            for district, metric in data.get("hoverData", {}).items():
                rows.append((state, year, quarter, district,
                             metric.get("registeredUsers", metric.get("registeredCount")),
                             metric.get("appOpens")))
        else:
            for district in data.get("hoverDataList", []):
                metric = district["metric"][0]
                rows.append((state, year, quarter, district["name"],
                             metric["count"], metric.get("amount")))
    insert_rows(connection, table, rows)


def load_top(connection, root, kind, table):
    rows = []
    folder = root / "data" / "top" / kind / "country" / "india"
    for state, year, quarter, data in read_files(folder):
        for entity_type in ["states", "districts", "pincodes"]:
            for item in data.get(entity_type) or []:
                if kind == "user":
                    name = str(item["name"]) if item["name"] is not None else None
                    rows.append((state, year, quarter, entity_type, name,
                                 item.get("registeredUsers", item.get("registeredCount"))))
                else:
                    metric = item["metric"]
                    name = str(item["entityName"]) if item["entityName"] is not None else None
                    rows.append((state, year, quarter, entity_type, name,
                                 metric["count"], metric.get("amount")))
    insert_rows(connection, table, rows)


def build_database(root):
    """Build a temporary database, then replace the old file after success."""
    DATABASE.parent.mkdir(exist_ok=True)
    temporary = DATABASE.with_suffix(".tmp")
    if temporary.exists():
        temporary.unlink()
    connection = sqlite3.connect(temporary)
    try:
        connection.executescript((BASE_DIR / "schema.sql").read_text(encoding="utf-8"))
        for kind, aggregate, district, top in [
            ("transaction", "aggregated_transaction", "map_map", "top_map"),
            ("user", "aggregated_user", "map_user", "top_user"),
            ("insurance", "aggregated_insurance", "map_insurance", "top_insurance"),
        ]:
            if not (root / "data" / "aggregated" / kind).exists():
                raise ValueError(f"Missing {kind} data. Use the documented legacy snapshot.")
            load_aggregated(connection, root, kind, aggregate)
            load_map(connection, root, kind, district)
            load_top(connection, root, kind, top)
            for table in [aggregate, district, top]:
                count = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                print(f"{table}: {count:,} rows")
        connection.commit()
    finally:
        connection.close()
    temporary.replace(DATABASE)
    commit = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    source_url = subprocess.check_output(["git", "-C", str(root), "remote", "get-url", "origin"], text=True).strip()
    metadata = {"source_url": source_url, "commit": commit,
                "dataset": "Legacy PhonePe Pulse snapshot; never mixed with the 2026 restatement",
                "loaded_at_utc": datetime.now(timezone.utc).isoformat()}
    (DATABASE.parent / "source.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, help="Path to a cloned legacy Pulse repository")
    args = parser.parse_args()
    root = args.source or BASE_DIR / "data" / "pulse"
    if args.source is None:
        if not root.exists():
            subprocess.run(["git", "clone", SOURCE_URL, str(root)], check=True)
        subprocess.run(["git", "-C", str(root), "checkout", SOURCE_COMMIT], check=True)
    build_database(root.resolve())
