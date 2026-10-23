import pytest

from app import db, pipeline


@pytest.fixture()
def db_path(tmp_path):
    p = str(tmp_path / "t.db")
    result = pipeline.run("data/sales_raw.csv", p)
    assert result == {"read": 12, "loaded": 9, "dropped": 3}
    return p


def test_sql_aggregates(db_path):
    conn = db.connect(db_path)
    regions = {r["region"]: r for r in db.revenue_by_region(conn)}
    assert regions["East"]["revenue"] == pytest.approx(366.93)
    assert db.monthly_revenue(conn)[0]["month"] == "2025-01"
    assert db.top_products(conn, 1)[0]["product"] == "Gizmo"


def test_api(db_path):
    fastapi_testclient = pytest.importorskip("fastapi.testclient")
    from app.main import create_app

    client = fastapi_testclient.TestClient(create_app(db_path))
    assert client.get("/health").json() == {"status": "ok"}
    assert len(client.get("/api/revenue/by-region").json()) == 4
    assert len(client.get("/api/products/top?limit=2").json()) == 2
    assert "Revenue by region" in client.get("/").text
