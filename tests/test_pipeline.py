import json
from pathlib import Path

import pandas as pd

from src.pipeline import run_pipeline


def test_pipeline_counts_and_partitions(tmp_path):
    counts = run_pipeline(base_dir=tmp_path)
    assert counts["bronze_rows"] == 110
    assert counts["silver_rows"] == 103
    assert counts["quality_passed"] is True
    assert abs(counts["silver_total"] - counts["gold_total"]) < 0.01
    # Partition directories exist, mimicking S3 year=/month=/day= keys.
    bronze = tmp_path / "lake" / "bronze" / "orders"
    partitions = [p for p in bronze.rglob("day=*") if p.is_dir()]
    assert partitions, "no day partitions found"
    silver = pd.read_parquet(tmp_path / "lake" / "silver" / "orders.parquet")
    assert silver["order_id"].is_unique
    assert silver["order_id"].notna().all()
    assert (silver["amount"] >= 0).all()
    # Late rows are present in silver despite earlier order_date.
    assert {"O3000", "O3001", "O3002"} <= set(silver["order_id"])
    # Duplicates counted once, at the latest amount.
    assert "O1000" in set(silver["order_id"])
    report = json.loads((tmp_path / "outputs" / "quality_report.json").read_text())
    assert report["passed"] is True
    gold = pd.read_csv(tmp_path / "outputs" / "gold" / "daily_revenue.csv")
    assert round(gold["revenue"].sum(), 2) == round(silver["amount"].sum(), 2)
