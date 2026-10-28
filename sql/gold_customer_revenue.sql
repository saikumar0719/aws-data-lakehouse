-- Athena / Presto SQL: gold customer revenue from curated orders.
SELECT customer_id,
       SUM(amount) AS revenue,
       COUNT(order_id) AS order_count
FROM curated_orders
GROUP BY customer_id
ORDER BY revenue DESC;
