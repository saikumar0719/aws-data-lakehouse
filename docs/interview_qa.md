# Recruiter Q&A — short answers, grounded in this code

**What does this project do?**
It turns messy shop orders into clean daily, customer, and product
revenue reports: S3 raw → Glue catalog → curated Parquet → Athena SQL.

**How do you handle late-arriving data?**
Late rows have an earlier order date but a later ingestion date.
They land in their order-date partition and silver is rebuilt from
all bronze on every run, so a re-run picks them up and corrects gold.

**How do you handle duplicates?**
Silver keeps only the latest row per order_id, ordered by updated_at
(`ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC)
= 1` in `sql/curated_orders.sql`), and a quality check asserts no
duplicate order_id remains in silver.

**How do you control Athena cost?**
Partition by year/month/day, store as compressed Parquet, and query
only the partitions needed. Terraform also moves raw data to
Standard-IA after 30 days.

**How does data quality gate the pipeline?**
`src/quality.py` checks null order_ids, duplicate order_ids, negative
amounts, silver ≤ bronze, and gold revenue reconciling to silver. It
writes `outputs/quality_report.json` and raises on any breach, so
gold is never published from failed data.

**Why Parquet?**
Columnar and compressed: queries read only the columns they need,
which is faster and cheaper than CSV in Athena.

**Why a Glue catalog?**
Glue stores table/schema definitions pointing at S3. It moves no
data, but lets Athena, Spark, and other engines share the same tables.

**What would you change in real AWS?**
Replace the local Python steps with Glue jobs or EMR/Spark for scale,
add S3 event triggers or an Airflow sensor for new partitions, add
partition-level incremental loads instead of full silver rebuilds,
and add alerting (for example, SNS) on quality-gate failure. The
local version is honest about this: it is built and tested locally,
not production.
