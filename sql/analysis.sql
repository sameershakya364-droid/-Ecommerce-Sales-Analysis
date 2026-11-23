-- Run after src/load_sqlite.py. Revenue below is item price; freight excluded.

-- 1. Order status distribution
SELECT order_status, COUNT(*) AS orders
FROM orders GROUP BY order_status ORDER BY orders DESC;

-- 2. Monthly order volume
SELECT substr(order_purchase_timestamp,1,7) AS month,
       COUNT(DISTINCT order_id) AS orders
FROM orders WHERE order_purchase_timestamp IS NOT NULL
GROUP BY month ORDER BY month;

-- 3. Top product categories by item revenue
SELECT COALESCE(t.product_category_name_english,p.product_category_name,'unknown') AS category,
       ROUND(SUM(oi.price),2) AS item_revenue,
       COUNT(*) AS units,
       COUNT(DISTINCT oi.order_id) AS orders
FROM order_items oi
LEFT JOIN products p ON oi.product_id=p.product_id
LEFT JOIN category_translation t ON p.product_category_name=t.product_category_name
GROUP BY category ORDER BY item_revenue DESC LIMIT 15;

-- 4. Top customer states by orders
SELECT c.customer_state, COUNT(DISTINCT o.order_id) AS orders
FROM orders o JOIN customers c ON o.customer_id=c.customer_id
GROUP BY c.customer_state ORDER BY orders DESC LIMIT 10;

-- 5. Payment methods
SELECT payment_type, COUNT(*) AS payment_records,
       ROUND(SUM(payment_value),2) AS payment_value
FROM payments GROUP BY payment_type ORDER BY payment_value DESC;

-- 6. Average delivery days for delivered orders
SELECT ROUND(AVG(julianday(order_delivered_customer_date)-
                 julianday(order_purchase_timestamp)),2) AS avg_delivery_days
FROM orders
WHERE order_status='delivered'
AND order_delivered_customer_date IS NOT NULL
AND order_purchase_timestamp IS NOT NULL;
