-- Athena / Presto SQL: gold product revenue from curated orders.
SELECT product_id,
       SUM(amount) AS revenue,
       SUM(quantity) AS total_quantity,
       COUNT(order_id) AS order_count
FROM curated_orders
GROUP BY product_id
ORDER BY revenue DESC;
