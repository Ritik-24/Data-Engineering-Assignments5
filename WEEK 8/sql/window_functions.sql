-- 7. Running Totals with Window Functions
-- Calculate running total of revenue per region, ordered by date
WITH DailyRegionRevenue AS (
    SELECT 
        o.region_code,
        strftime('%Y-%m-%d', o.order_date) AS order_day,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS daily_revenue
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    GROUP BY o.region_code, order_day
)
SELECT 
    region_code,
    order_day,
    ROUND(daily_revenue, 2) AS daily_revenue,
    ROUND(SUM(daily_revenue) OVER (PARTITION BY region_code ORDER BY order_day), 2) AS running_total
FROM DailyRegionRevenue
ORDER BY region_code, order_day;

-- 8. Ranking with DENSE_RANK
-- Rank products by total revenue inside each category
WITH ProductRevenue AS (
    SELECT 
        p.category,
        p.product_name,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS total_revenue
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY p.category, p.product_id, p.product_name
)
SELECT 
    category,
    product_name,
    ROUND(total_revenue, 2) AS total_revenue,
    DENSE_RANK() OVER (PARTITION BY category ORDER BY total_revenue DESC) AS rank_in_category
FROM ProductRevenue
ORDER BY category, rank_in_category;

-- 9. LAG/LEAD Analysis
-- Calculate days between consecutive orders per customer and flag "At Risk"
WITH CustomerOrderDates AS (
    SELECT 
        customer_id,
        order_date,
        LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) AS previous_order_date
    FROM orders
),
GapsCalculated AS (
    SELECT 
        customer_id,
        order_date,
        previous_order_date,
        CASE 
            WHEN previous_order_date IS NULL THEN 0
            ELSE CAST((julianday(order_date) - julianday(previous_order_date)) AS INT)
        END AS days_gap
    FROM CustomerOrderDates
)
SELECT 
    customer_id,
    order_date,
    previous_order_date,
    days_gap,
    CASE 
        WHEN AVG(days_gap) OVER (PARTITION BY customer_id) > 30 THEN 'At Risk'
        ELSE 'Active'
    END AS status_flag
FROM GapsCalculated
ORDER BY customer_id, order_date;

-- 10. CTE with Multiple Levels
-- Find customer counts grouped by monthly spend categories
WITH MonthlyCustomerSpend AS (
    SELECT 
        o.customer_id,
        strftime('%Y-%m', o.order_date) AS spend_month,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS total_spend
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    GROUP BY o.customer_id, spend_month
),
SegmentedCustomers AS (
    SELECT 
        customer_id,
        spend_month,
        CASE 
            WHEN total_spend > 10000 THEN 'High'
            WHEN total_spend BETWEEN 5000 AND 10000 THEN 'Medium'
            ELSE 'Low'
        END AS spend_tier
    FROM MonthlyCustomerSpend
)
SELECT 
    spend_month,
    spend_tier,
    COUNT(customer_id) AS customer_count
FROM SegmentedCustomers
GROUP BY spend_month, spend_tier
ORDER BY spend_month DESC, spend_tier DESC;

-- 11. NTILE for Segmentation
-- Divide customers into 4 quartiles based on lifetime value
WITH CustomerLTV AS (
    SELECT 
        o.customer_id,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS total_value
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    GROUP BY o.customer_id
),
Quartiles AS (
    SELECT 
        customer_id,
        total_value,
        NTILE(4) OVER (ORDER BY total_value DESC) AS quartile
    FROM CustomerLTV
)
SELECT 
    customer_id,
    ROUND(total_value, 2) AS total_value,
    quartile,
    CASE 
        WHEN quartile = 1 THEN 'Platinum'
        WHEN quartile = 2 THEN 'Gold'
        WHEN quartile = 3 THEN 'Silver'
        ELSE 'Bronze'
    END AS quartile_label
FROM Quartiles
ORDER BY total_value DESC;