"""CLI entry: python -m app.pipeline data/sales_raw.csv sales.db"""
from __future__ import annotations

import sys

from . import cleaning, db


def run(csv_path: str, db_path: str) -> dict:
    raw = cleaning.read_csv(csv_path)
    cleaned = list(cleaning.clean_rows(raw))
    conn = db.connect(db_path)
    loaded = db.load_sales(conn, cleaned)
    conn.close()
    return {"read": len(raw), "loaded": loaded, "dropped": len(raw) - loaded}


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: python -m app.pipeline <csv> <db>")
    print(run(sys.argv[1], sys.argv[2]))
