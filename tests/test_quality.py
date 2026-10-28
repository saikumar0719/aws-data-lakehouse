import pandas as pd

from src.quality import check_quality

BRONZE = pd.DataFrame({"order_id": ["O1", "O1", "O2"], "amount": [10.0, 12.0, 20.0]})
SILVER_GOOD = pd.DataFrame({"order_id": ["O1", "O2"], "amount": [12.0, 20.0]})
GOLD_GOOD = pd.DataFrame({"order_date": ["2026-10-01"], "revenue": [32.0]})


def test_quality_passes_on_clean_data():
    report = check_quality(BRONZE, SILVER_GOOD, GOLD_GOOD)
    assert report["passed"] is True
    assert report["silver_total"] == 32.0


def test_quality_fails_on_duplicate_silver():
    bad_silver = pd.DataFrame({"order_id": ["O1", "O1"], "amount": [12.0, 12.0]})
    report = check_quality(BRONZE, bad_silver, GOLD_GOOD)
    assert report["passed"] is False
    assert report["checks"]["no_duplicate_order_id_in_silver"] is False


def test_quality_fails_on_reconciliation_mismatch():
    bad_gold = pd.DataFrame({"order_date": ["2026-10-01"], "revenue": [999.0]})
    report = check_quality(BRONZE, SILVER_GOOD, bad_gold)
    assert report["passed"] is False
    assert report["checks"]["gold_revenue_reconciles_to_silver"] is False
