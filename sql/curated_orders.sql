-- Athena / Presto SQL: curated (silver) orders from raw (bronze).
-- In AWS, raw_orders is the Glue table over S3 raw; locally, the
-- curated_orders view is built from the silver Parquet file.
-- Keeps only the latest row per order_id, drops null/negative amounts.
SELECT order_id, customer_id, product_id, order_date, ingestion_date,
       updated_at, quantity, unit_price, amount, status
FROM (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY order_id ORDER BY updated_at DESC
           ) AS rn
    FROM raw_orders
    WHERE amount IS NOT NULL AND amount >= 0 AND quantity > 0
) ranked
WHERE rn = 1;
