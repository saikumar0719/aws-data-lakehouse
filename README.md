# AWS Data Lakehouse — S3 + Glue + Athena-style SQL + Airflow

## In plain language

A shop takes messy orders every day: duplicate orders, a missing price,
an order that arrives days late. Managers still need one trustworthy
report: how much did we sell, by day, by customer, and by product?

This project turns that messy shop data into clean, trustworthy reports:

```
source orders
  -> S3 raw (bronze, partitioned Parquet)
  -> Glue catalog (table definitions, no data movement)
  -> curated Parquet (silver, deduplicated and checked)
  -> Athena-style SQL (gold aggregates)
  -> daily / customer / product revenue reports
```

It is the AWS counterpart to Sai's other two portfolio projects:
GCP streaming (Kafka → Pub/Sub → Dataflow → BigQuery) and the dbt
lakehouse on BigQuery. This one shows the AWS lakehouse pattern
recruiters ask about most: S3 partitioning, a Glue catalog, and
Athena-style SQL over Parquet.

**Honest status: built and tested locally, not production.**
Locally, DuckDB + Parquet mimic S3 / Glue / Athena with zero cloud
cost. The Terraform in `terraform/` is the real AWS production path —
it is code only and has NOT been applied to AWS, so no cloud resources
were created or charged for this project.

## Pipeline order

1. `src/generate_data.py` — deterministic sample orders, customers,
   and products (seed 42, so every run gives the same data).
2. Bronze — raw orders written as Parquet partitioned by
   `year=/month=/day=` of the order date, mimicking S3 keys such as
   `s3://<raw-bucket>/orders/year=2026/month=10/day=20/part-....parquet`.
3. Silver / curated — deduplicate, drop bad rows, keep the latest
   version of each order.
4. Gold — daily revenue, customer revenue, and product revenue,
   written as Parquet and CSV.
5. Quality gate — the pipeline fails if any check fails, so bad data
   never reaches the gold reports.

## Run it locally (5 steps)

```bash
cd aws-data-lakehouse
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. python run_pipeline.py
PYTHONPATH=. python -m pytest -q
```

Or, in one step: `bash scripts/run_local.sh`

Expected output (see `outputs/quality_report.json` after a run):
bronze 110 rows, silver 103 rows, gold daily revenue reconciles
exactly to the silver total. Row counts are printed by
`run_pipeline.py` on every run.

Outputs after a run:

- `lake/bronze/orders/` — partitioned Parquet (S3 raw, local mirror)
- `lake/silver/orders.parquet` — curated orders
- `lake/gold/*.parquet` and `outputs/gold/*.csv` — gold reports
- `outputs/quality_report.json` — quality-gate result

## Production AWS path (documented, not run)

1. Apply `terraform/` — creates versioned S3 buckets for raw, curated,
   and gold, a Glue database, an Athena workgroup whose query results
   go to S3, and a least-privilege IAM role for the pipeline.
2. Land raw files in the raw bucket under the same
   `year=/month=/day=` partition layout used locally.
3. Register the raw and curated tables in Glue (the SQL in `sql/`
   is written in Athena/Presto style and maps to those Glue tables).
4. Run the Airflow DAG in `airflow/dags/aws_lakehouse_dag.py` daily
   (in real AWS, replace the local Python steps with Glue jobs or
   EMR/Spark steps; the task order and the quality gate stay the same).
5. Query gold tables in Athena; Athena charges per byte scanned, so
   partitioning and Parquet keep queries cheap (see Cost control).

## Design answers, grounded in the code

- **Late-arriving data:** late rows carry an earlier `order_date` but
  a later `ingestion_date`. Bronze keeps them in their order-date
  partition, and silver is rebuilt from all of bronze on every run,
  so a re-run picks the late rows up and gold totals are corrected —
  it does not silently drop them.
- **Duplicate handling:** silver sorts by `updated_at` and keeps only
  the latest row per `order_id` (`ROW_NUMBER() OVER (PARTITION BY
  order_id ORDER BY updated_at DESC) = 1` in `sql/curated_orders.sql`),
  so a re-sent order is counted once, at its latest amount.
- **Cost control:** bronze is partitioned by year/month/day and stored
  as compressed Parquet, so Athena scans only the partitions a query
  needs; Terraform adds a lifecycle rule moving raw data to
  Standard-IA after 30 days.
- **Data-quality gating:** `src/quality.py` checks no null
  `order_id`, no duplicate `order_id` in silver, no negative amounts,
  silver count ≤ bronze count, and gold revenue reconciling to silver.
  It writes `outputs/quality_report.json` and raises on any breach,
  so gold is never published from failed data.

## What to say in an interview

Run the local steps once first, then describe it from doing it, not
from reading this file. See `docs/interview_qa.md` for the short
recruiter Q&A, and `docs/architecture.md` for the diagram and
partition strategy.
