"""SQLite persistence. Plain SQL on purpose; swap the connection for psycopg to use Postgres."""
from __future__ import annotations

import sqlite3
from typing import Iterable

from .cleaning import Sale

SCHEMA = """
CREATE TABLE IF NOT EXISTS sales (
    order_id   INTEGER PRIMARY KEY,
    sale_date  TEXT    NOT NULL,
    region     TEXT    NOT NULL,
    product    TEXT    NOT NULL,
    quantity   INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL    NOT NULL CHECK (unit_price > 0)
);
CREATE INDEX IF NOT EXISTS idx_sales_region ON sales(region);
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);
"""


def connect(path: str = "sales.db") -> sqlite3.Connection:
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def load_sales(conn: sqlite3.Connection, sales: Iterable[Sale]) -> int:
    rows = [(s.order_id, s.sale_date.isoformat(), s.region, s.product, s.quantity, s.unit_price) for s in sales]
    with conn:
        conn.executemany(
            "INSERT OR REPLACE INTO sales VALUES (?,?,?,?,?,?)", rows
        )
    return len(rows)


def revenue_by_region(conn: sqlite3.Connection) -> list[dict]:
    cur = conn.execute(
        """SELECT region, COUNT(*) AS orders, ROUND(SUM(quantity*unit_price),2) AS revenue
           FROM sales GROUP BY region ORDER BY revenue DESC"""
    )
    return [dict(r) for r in cur]


def monthly_revenue(conn: sqlite3.Connection) -> list[dict]:
    cur = conn.execute(
        """SELECT substr(sale_date,1,7) AS month, ROUND(SUM(quantity*unit_price),2) AS revenue
           FROM sales GROUP BY month ORDER BY month"""
    )
    return [dict(r) for r in cur]


def top_products(conn: sqlite3.Connection, limit: int = 3) -> list[dict]:
    cur = conn.execute(
        """SELECT product, SUM(quantity) AS units, ROUND(SUM(quantity*unit_price),2) AS revenue
           FROM sales GROUP BY product ORDER BY revenue DESC LIMIT ?""",
        (limit,),
    )
    return [dict(r) for r in cur]
