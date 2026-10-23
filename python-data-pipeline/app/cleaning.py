"""Pure functions that turn messy CSV rows into validated records."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable, Iterator

DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y")


@dataclass(frozen=True)
class Sale:
    order_id: int
    sale_date: date
    region: str
    product: str
    quantity: int
    unit_price: float


def parse_date(raw: str) -> date | None:
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw.strip(), fmt).date()
        except ValueError:
            continue
    return None


def clean_row(row: dict[str, str]) -> Sale | None:
    """Return a Sale, or None if the row is unusable."""
    try:
        order_id = int(row["order_id"])
        quantity = int(row["quantity"])
        unit_price = float(row["unit_price"])
    except (KeyError, ValueError, TypeError):
        return None
    sale_date = parse_date(row.get("date", ""))
    region = (row.get("region") or "").strip().title()
    product = (row.get("product") or "").strip().title()
    if sale_date is None or not region or not product:
        return None
    if quantity <= 0 or unit_price <= 0:
        return None
    return Sale(order_id, sale_date, region, product, quantity, unit_price)


def clean_rows(rows: Iterable[dict[str, str]]) -> Iterator[Sale]:
    """Clean rows, dropping invalid ones and duplicate order ids (first wins)."""
    seen: set[int] = set()
    for row in rows:
        sale = clean_row(row)
        if sale and sale.order_id not in seen:
            seen.add(sale.order_id)
            yield sale


def read_csv(path: str) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))
