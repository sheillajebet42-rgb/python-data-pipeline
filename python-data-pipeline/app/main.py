"""FastAPI service exposing analytics over the sales table, plus a tiny HTML dashboard."""
from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from . import db

DB_PATH = os.environ.get("SALES_DB", "sales.db")


def create_app(db_path: str | None = None) -> FastAPI:
    app = FastAPI(title="Sales Analytics API")
    conn = db.connect(db_path or DB_PATH)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/api/revenue/by-region")
    def by_region():
        return db.revenue_by_region(conn)

    @app.get("/api/revenue/monthly")
    def monthly():
        return db.monthly_revenue(conn)

    @app.get("/api/products/top")
    def top(limit: int = 3):
        return db.top_products(conn, max(1, min(limit, 50)))

    @app.get("/", response_class=HTMLResponse)
    def dashboard():
        return DASHBOARD

    return app


DASHBOARD = """<!doctype html><html><head><meta charset="utf-8"><title>Sales</title>
<style>body{font-family:system-ui;max-width:720px;margin:2rem auto;padding:0 1rem}
.bar{background:#4f46e5;color:#fff;padding:4px 8px;margin:4px 0;border-radius:4px;white-space:nowrap}</style></head>
<body><h1>Revenue by region</h1><div id="c">Loading…</div>
<script>
fetch('/api/revenue/by-region').then(r=>r.json()).then(d=>{
  const max=Math.max(...d.map(x=>x.revenue),1);
  document.getElementById('c').innerHTML=d.map(x=>
    `<div class="bar" style="width:${Math.max(x.revenue/max*100,8)}%">${x.region}: $${x.revenue.toFixed(2)}</div>`).join('');
});
</script></body></html>"""

app = create_app()
