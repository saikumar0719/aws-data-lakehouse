from pathlib import Path

import duckdb
import pandas as pd

from src.pipeline import run_pipeline

ROOT = Path(__file__).resolve().parent.parent


def test_gold_daily_sql_via_duckdb(tmp_path):
    run_pipeline(base_dir=tmp_path)
    silver_path = str(tmp_path / "lake" / "silver" / "orders.parquet")
    sql = (ROOT / "sql" / "gold_daily_revenue.sql").read_text(encoding="utf-8")
    con = duckdb.connect()
    con.execute(f"CREATE VIEW curated_orders AS SELECT * FROM read_parquet('{silver_path}')")
    result = con.execute(sql).fetchdf()
    silver = pd.read_parquet(silver_path)
    assert round(result["revenue"].sum(), 2) == round(silver["amount"].sum(), 2)
    assert len(result) == silver["order_date"].nunique()
    con.close()
