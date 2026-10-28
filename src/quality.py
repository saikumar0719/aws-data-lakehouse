"""Data-quality gate: fails loudly so bad data never reaches gold."""
import json
from pathlib import Path

import pandas as pd


def check_quality(bronze: pd.DataFrame, silver: pd.DataFrame, gold_daily: pd.DataFrame) -> dict:
    checks = {}
    checks["no_null_order_id_in_silver"] = bool(silver["order_id"].notna().all())
    checks["no_duplicate_order_id_in_silver"] = bool(not silver["order_id"].duplicated().any())
    checks["no_negative_amount_in_silver"] = bool((silver["amount"] >= 0).all())
    checks["silver_count_le_bronze_count"] = bool(len(silver) <= len(bronze))
    silver_total = round(float(silver["amount"].sum()), 2) if len(silver) else 0.0
    gold_total = round(float(gold_daily["revenue"].sum()), 2) if len(gold_daily) else 0.0
    checks["gold_revenue_reconciles_to_silver"] = abs(silver_total - gold_total) < 0.01
    report = {
        "passed": bool(all(checks.values())),
        "checks": checks,
        "bronze_rows": int(len(bronze)),
        "silver_rows": int(len(silver)),
        "silver_total": silver_total,
        "gold_total": gold_total,
    }
    return report


def write_report(report: dict, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "quality_report.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return path
