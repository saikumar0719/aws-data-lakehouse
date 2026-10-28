# Architecture

```
source orders (CSV / app)
        |
        v
S3 raw bucket  -- bronze, Parquet, partitioned:
  s3://<raw>/orders/year=2026/month=10/day=20/part-....parquet
        |
        v (Glue catalog registers the table; Glue moves no data)
Glue table: raw_orders
        |
        v (dedup by order_id, drop null/negative, quality gate)
S3 curated bucket -- silver Parquet
  Glue table: curated_orders
        |
        v (Athena / Presto SQL in sql/)
S3 gold bucket -- daily_revenue, customer_revenue, product_revenue
  (Parquet + CSV) -> reports / dashboards
        |
        v
Airflow DAG (daily, catchup=False, retries=2) orchestrates it all.
Locally, DuckDB + local folders stand in for S3 / Glue / Athena.
```

## Partition strategy

Bronze is partitioned by the order date (`year/month/day`), not by
ingestion date. A query for one day therefore scans only that day's
partition, which is how Athena cost stays low: Athena charges per
byte scanned, and partitioning + Parquet compression cut scanned
bytes sharply. Late rows land in their original order-date partition,
and silver is rebuilt from all bronze partitions on every run, so
late data corrects gold instead of being lost.

## Why Parquet, why Glue

Parquet is columnar and compressed, so analytical queries read only
the columns they need. Glue is only a catalog — table and schema
definitions pointing at S3 — so Athena, Spark, and other engines can
share the same tables without copying data.
