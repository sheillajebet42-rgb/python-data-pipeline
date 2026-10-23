from app.cleaning import clean_row, clean_rows, parse_date, read_csv


def row(**kw):
    base = dict(order_id="1", date="2025-01-01", region="north", product="widget", quantity="2", unit_price="5.0")
    base.update(kw)
    return base


def test_parse_date_formats():
    assert parse_date("2025-01-03").isoformat() == "2025-01-03"
    assert parse_date("03/01/2025").isoformat() == "2025-01-03"
    assert parse_date("garbage") is None


def test_normalizes_text():
    s = clean_row(row(region=" north ", product="WIDGET"))
    assert (s.region, s.product) == ("North", "Widget")


def test_rejects_bad_rows():
    assert clean_row(row(quantity="")) is None
    assert clean_row(row(unit_price="-1")) is None
    assert clean_row(row(date="nope")) is None
    assert clean_row(row(region="  ")) is None


def test_dedupes_first_wins():
    out = list(clean_rows([row(quantity="1"), row(quantity="9")]))
    assert len(out) == 1 and out[0].quantity == 1


def test_sample_file_counts():
    rows = read_csv("data/sales_raw.csv")
    cleaned = list(clean_rows(rows))
    # 12 raw rows: 1 blank qty, 1 negative price, 1 duplicate id -> 9 valid
    assert len(rows) == 12 and len(cleaned) == 9
