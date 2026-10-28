-- Athena / Presto SQL: gold daily revenue from curated orders.
SELECT order_date,
       SUM(amount) AS revenue,
       COUNT(order_id) AS order_count
FROM curated_orders
GROUP BY order_date
ORDER BY order_date;
