-- 12. Year-over-Year Comparison
WITH MonthlyRevenue AS (
    SELECT 
        CAST(strftime('%Y', o.order_date) AS INT) AS r_year,
        CAST(strftime('%m', o.order_date) AS INT) AS r_month,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS revenue
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    GROUP BY r_year, r_month
)
SELECT 
    curr.r_year AS year,
    curr.r_month AS month,
    ROUND(curr.revenue, 2) AS revenue,
    ROUND(prev.revenue, 2) AS prev_year_revenue,
    ROUND(((curr.revenue - COALESCE(prev.revenue, 0)) / NULLIF(prev.revenue, 0)) * 100.0, 2) AS yoy_growth_percent
FROM MonthlyRevenue curr
LEFT JOIN MonthlyRevenue prev ON curr.r_year = prev.r_year + 1 AND curr.r_month = prev.r_month
ORDER BY year DESC, month DESC;

-- 13. First/Last Value Analysis (Category Shift Detection)
WITH OrderedPurchases AS (
    SELECT 
        o.customer_id,
        p.category,
        o.order_date,
        ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_date ASC) AS rn_first,
        ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_date DESC) AS rn_last
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    JOIN products p ON oi.product_id = p.product_id
),
FirstCategory AS (
    SELECT customer_id, category AS first_purchased_category FROM OrderedPurchases WHERE rn_first = 1
),
LastCategory AS (
    SELECT customer_id, category AS most_recent_category FROM OrderedPurchases WHERE rn_last = 1
)
SELECT 
    f.customer_id,
    f.first_purchased_category,
    l.most_recent_category,
    CASE 
        WHEN f.first_purchased_category != l.most_recent_category THEN 'Yes'
        ELSE 'No'
    END AS category_shift
FROM FirstCategory f
JOIN LastCategory l ON f.customer_id = l.customer_id;

-- 14. Cumulative Distribution (Pareto Principle Top N% Revenue Check)
WITH CustomerRevenue AS (
    SELECT 
        o.customer_id,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS customer_revenue
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    GROUP BY o.customer_id
),
TotalSystemRevenue AS (
    SELECT SUM(customer_revenue) AS total_rev FROM CustomerRevenue
),
RunningRevenue AS (
    SELECT 
        customer_id,
        customer_revenue,
        SUM(customer_revenue) OVER (ORDER BY customer_revenue DESC) AS cum_revenue
    FROM CustomerRevenue
)
SELECT 
    r.customer_id,
    ROUND(r.customer_revenue, 2) AS revenue,
    ROUND(r.cum_revenue, 2) AS cumulative_revenue,
    ROUND((r.cum_revenue / t.total_rev) * 100.0, 2) AS cumulative_percent
FROM RunningRevenue r
CROSS JOIN TotalSystemRevenue t
ORDER BY revenue DESC;

-- 15. Complex CTE: Cohort Analysis
WITH CohortBase AS (
    SELECT 
        customer_id,
        strftime('%Y-%m', MIN(order_date)) AS cohort_month
    FROM orders
    GROUP BY customer_id
),
ActivityBase AS (
    SELECT 
        o.customer_id,
        strftime('%Y-%m', o.order_date) AS activity_month,
        c.cohort_month,
        (CAST(strftime('%Y', o.order_date) AS INT) - CAST(strftime('%Y', c.cohort_month) AS INT)) * 12 +
        (CAST(strftime('%m', o.order_date) AS INT) - CAST(strftime('%m', c.cohort_month) AS INT)) AS month_number
    FROM orders o
    JOIN CohortBase c ON o.customer_id = c.customer_id
),
CohortSizes AS (
    SELECT cohort_month, COUNT(DISTINCT customer_id) AS cohort_size FROM CohortBase GROUP BY cohort_month
),
RetentionCounts AS (
    SELECT 
        cohort_month,
        month_number,
        COUNT(DISTINCT customer_id) AS active_customers
    FROM ActivityBase
    WHERE month_number BETWEEN 0 AND 3
    GROUP BY cohort_month, month_number
)
SELECT 
    r.cohort_month,
    s.cohort_size,
    r.month_number,
    r.active_customers,
    ROUND((CAST(r.active_customers AS REAL) / s.cohort_size) * 100.0, 2) AS retention_rate
FROM RetentionCounts r
JOIN CohortSizes s ON r.cohort_month = s.cohort_month
ORDER BY r.cohort_month, r.month_number;

-- 16. Self-Join with Window Function (Frequently Bought Together Pairs)
WITH ProductPairs AS (
    SELECT 
        a.product_id AS prod_a_id,
        pa.product_name AS product_a,
        b.product_id AS prod_b_id,
        pb.product_name AS product_b,
        a.order_id
    FROM order_items a
    JOIN order_items b ON a.order_id = b.order_id AND a.product_id < b.product_id
    JOIN products pa ON a.product_id = pa.product_id
    JOIN products pb ON b.product_id = pb.product_id
)
SELECT 
    product_a,
    product_b,
    COUNT(order_id) AS times_bought_together
FROM ProductPairs
GROUP BY product_a, product_b
ORDER BY times_bought_together DESC
LIMIT 10;