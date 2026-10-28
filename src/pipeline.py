"""Bronze -> silver -> gold pipeline.

Local mirror of the AWS path: bronze is Parquet partitioned by
year/month/day (S3 keys), silver is deduplicated curated Parquet,
gold is Athena-style aggregates written as Parquet and CSV.
Silver is rebuilt from all of bronze on every run, so late-arriving
rows are picked up on re-run.
"""
from pathlib import Path

import pandas as pd

from src.generate_data import generate_orders
from src.quality import check_quality, write_report


def _add_partitions(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    dates = pd.to_datetime(df["order_date"])
    df["year"] = dates.dt.year
    df["month"] = dates.dt.month
    df["day"] = dates.dt.day
    return df


def build_silver(bronze: pd.DataFrame) -> pd.DataFrame:
    silver = bronze.copy()
    silver = silver.sort_values("updated_at")
    silver = silver.drop_duplicates(subset=["order_id"], keep="last")
    silver = silver[silver["amount"].notna() & (silver["amount"] >= 0) & (silver["quantity"] > 0)]
    return silver.reset_index(drop=True)


def build_gold(silver: pd.DataFrame) -> dict:
    daily = (
        silver.groupby("order_date", as_index=False)
        .agg(revenue=("amount", "sum"), order_count=("order_id", "count"))
        .sort_values("order_date")
    )
    daily["revenue"] = daily["revenue"].round(2)
    customer = (
        silver.groupby("customer_id", as_index=False)
        .agg(revenue=("amount", "sum"), order_count=("order_id", "count"))
        .sort_values("revenue", ascending=False)
    )
    customer["revenue"] = customer["revenue"].round(2)
    product = (
        silver.groupby("product_id", as_index=False)
        .agg(revenue=("amount", "sum"), total_quantity=("quantity", "sum"), order_count=("order_id", "count"))
        .sort_values("revenue", ascending=False)
    )
    product["revenue"] = product["revenue"].round(2)
    return {"daily_revenue": daily, "customer_revenue": customer, "product_revenue": product}


def run_pipeline(base_dir: Path | None = None) -> dict:
    base = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
    lake = base / "lake"
    outputs = base / "outputs"
    bronze_dir = lake / "bronze" / "orders"
    silver_path = lake / "silver" / "orders.parquet"
    gold_dir = lake / "gold"
    gold_csv_dir = outputs / "gold"
    for d in (bronze_dir, silver_path.parent, gold_dir, gold_csv_dir):
        d.mkdir(parents=True, exist_ok=True)

    raw = generate_orders()
    bronze = _add_partitions(raw)
    # Partitioned write mimics S3 year=/month=/day= keys.
    bronze.to_parquet(bronze_dir, partition_cols=["year", "month", "day"], index=False)

    silver = build_silver(bronze)
    silver.drop(columns=["year", "month", "day"], errors="ignore").to_parquet(silver_path, index=False)

    gold = build_gold(silver)
    for name, frame in gold.items():
        frame.to_parquet(gold_dir / f"{name}.parquet", index=False)
        frame.to_csv(gold_csv_dir / f"{name}.csv", index=False)

    report = check_quality(bronze, silver, gold["daily_revenue"])
    write_report(report, outputs)
    if not report["passed"]:
        raise ValueError(f"Quality gate failed: {report['checks']}")
    return {
        "bronze_rows": int(len(bronze)),
        "silver_rows": int(len(silver)),
        "gold_daily_rows": int(len(gold["daily_revenue"])),
        "gold_customer_rows": int(len(gold["customer_revenue"])),
        "gold_product_rows": int(len(gold["product_revenue"])),
        "silver_total": report["silver_total"],
        "gold_total": report["gold_total"],
        "quality_passed": report["passed"],
    }
