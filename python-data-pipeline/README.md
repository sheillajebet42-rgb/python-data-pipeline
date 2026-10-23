# Python Data Pipeline + Analytics API
![CI](https://github.com/YOUR_USER/python-data-pipeline/actions/workflows/ci.yml/badge.svg)

Cleans a messy sales CSV, loads it into SQL, and serves analytics through FastAPI with a small HTML dashboard.

```
CSV -> cleaning.py (validate, normalize, dedupe) -> db.py (SQL schema + aggregates) -> main.py (FastAPI + dashboard)
```

## Run
```bash
pip install -r requirements.txt
python -m app.pipeline data/sales_raw.csv sales.db   # {'read': 12, 'loaded': 9, 'dropped': 3}
uvicorn app.main:app --reload                         # http://localhost:8000
```
Endpoints: `/api/revenue/by-region`, `/api/revenue/monthly`, `/api/products/top?limit=3`, `/health`.

## Test
```bash
pip install -r requirements-dev.txt && pytest
```

## Design decisions
- **Cleaning is pure functions** (no I/O), so rules are unit-tested without a database.
- **Constraints live in SQL too** (`CHECK`, primary key), so bad data cannot slip in through another code path.
- **`INSERT OR REPLACE`** makes the pipeline idempotent: re-running it does not duplicate rows.
- **SQLite for zero setup**; the SQL is standard enough to move to Postgres by swapping the connection (and `?` for `%s`).
