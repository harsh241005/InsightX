-- ============================================================
-- InsightX — BigQuery Analytics Table Creation
-- Run these queries in BigQuery Console one at a time
-- Dataset: ecommerce
-- ============================================================

-- 1. Monthly Revenue Summary
CREATE OR REPLACE TABLE `ecommerce.monthly_revenue` AS
SELECT
    DATE_TRUNC(CAST(o.order_purchase_timestamp AS DATE), MONTH) as month,
    COUNT(DISTINCT o.order_id) as total_orders,
    COUNT(DISTINCT o.customer_id) as unique_customers,
    ROUND(SUM(oi.price + oi.freight_value), 2) as total_revenue,
    ROUND(AVG(oi.price + oi.freight_value), 2) as avg_order_value,
    ROUND(SUM(oi.price), 2) as product_revenue,
    ROUND(SUM(oi.freight_value), 2) as freight_revenue
FROM `ecommerce.orders` o
JOIN `ecommerce.order_items` oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY 1
ORDER BY 1;

-- 2. Category Performance
CREATE OR REPLACE TABLE `ecommerce.category_performance` AS
SELECT
    COALESCE(ct.product_category_name_english, p.product_category_name, 'Unknown') as category,
    COUNT(DISTINCT oi.order_id) as total_orders,
    ROUND(SUM(oi.price), 2) as total_revenue,
    ROUND(AVG(oi.price), 2) as avg_price,
    ROUND(SUM(oi.freight_value), 2) as total_freight,
    COUNT(DISTINCT oi.seller_id) as seller_count
FROM `ecommerce.order_items` oi
JOIN `ecommerce.products` p ON oi.product_id = p.product_id
LEFT JOIN `ecommerce.category_translation` ct ON p.product_category_name = ct.product_category_name
JOIN `ecommerce.orders` o ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY 1
ORDER BY total_revenue DESC;

-- 3. Customer Metrics
CREATE OR REPLACE TABLE `ecommerce.customer_metrics` AS
SELECT
    c.customer_unique_id,
    c.customer_state,
    c.customer_city,
    COUNT(DISTINCT o.order_id) as total_orders,
    ROUND(SUM(oi.price + oi.freight_value), 2) as total_spend,
    ROUND(AVG(oi.price + oi.freight_value), 2) as avg_order_value,
    MIN(CAST(o.order_purchase_timestamp AS DATE)) as first_purchase,
    MAX(CAST(o.order_purchase_timestamp AS DATE)) as last_purchase,
    DATE_DIFF(MAX(CAST(o.order_purchase_timestamp AS DATE)),
              MIN(CAST(o.order_purchase_timestamp AS DATE)), MONTH) + 1 as active_months,
    ROUND(AVG(r.review_score), 1) as avg_review_score
FROM `ecommerce.customers` c
JOIN `ecommerce.orders` o ON c.customer_id = o.customer_id
JOIN `ecommerce.order_items` oi ON o.order_id = oi.order_id
LEFT JOIN `ecommerce.order_reviews` r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
GROUP BY 1, 2, 3;

-- 4. Executive KPIs
CREATE OR REPLACE TABLE `ecommerce.executive_kpis` AS
SELECT
    ROUND(SUM(oi.price + oi.freight_value), 2) as total_revenue,
    COUNT(DISTINCT o.order_id) as total_orders,
    COUNT(DISTINCT o.customer_id) as total_customers,
    COUNT(DISTINCT oi.seller_id) as total_sellers,
    ROUND(AVG(oi.price + oi.freight_value), 2) as avg_order_value,
    ROUND(AVG(r.review_score), 2) as avg_review_score
FROM `ecommerce.orders` o
JOIN `ecommerce.order_items` oi ON o.order_id = oi.order_id
LEFT JOIN `ecommerce.order_reviews` r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered';

-- 5. Regional Performance
CREATE OR REPLACE TABLE `ecommerce.regional_performance` AS
SELECT
    c.customer_state as state,
    COUNT(DISTINCT o.order_id) as total_orders,
    COUNT(DISTINCT c.customer_unique_id) as total_customers,
    ROUND(SUM(oi.price + oi.freight_value), 2) as total_revenue,
    ROUND(AVG(oi.price + oi.freight_value), 2) as avg_order_value
FROM `ecommerce.customers` c
JOIN `ecommerce.orders` o ON c.customer_id = o.customer_id
JOIN `ecommerce.order_items` oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY 1
ORDER BY total_revenue DESC;

-- 6. Cohort Analysis
CREATE OR REPLACE TABLE `ecommerce.cohort_analysis` AS
WITH first_purchase AS (
    SELECT
        c.customer_unique_id,
        DATE_TRUNC(MIN(CAST(o.order_purchase_timestamp AS DATE)), MONTH) as cohort_month
    FROM `ecommerce.customers` c
    JOIN `ecommerce.orders` o ON c.customer_id = o.customer_id
    WHERE o.order_status = 'delivered'
    GROUP BY 1
),
orders_with_cohort AS (
    SELECT
        fp.customer_unique_id,
        fp.cohort_month,
        DATE_TRUNC(CAST(o.order_purchase_timestamp AS DATE), MONTH) as order_month,
        DATE_DIFF(DATE_TRUNC(CAST(o.order_purchase_timestamp AS DATE), MONTH),
                  fp.cohort_month, MONTH) as months_since_first
    FROM first_purchase fp
    JOIN `ecommerce.customers` c ON fp.customer_unique_id = c.customer_unique_id
    JOIN `ecommerce.orders` o ON c.customer_id = o.customer_id
    WHERE o.order_status = 'delivered'
)
SELECT
    cohort_month,
    months_since_first,
    COUNT(DISTINCT customer_unique_id) as customers
FROM orders_with_cohort
GROUP BY 1, 2
ORDER BY 1, 2;

-- 7. Payment Analysis
CREATE OR REPLACE TABLE `ecommerce.payment_analysis` AS
SELECT
    op.payment_type,
    COUNT(DISTINCT o.order_id) as total_orders,
    ROUND(SUM(op.payment_value), 2) as total_revenue,
    ROUND(AVG(op.payment_value), 2) as avg_payment,
    ROUND(AVG(op.payment_installments), 1) as avg_installments
FROM `ecommerce.order_payments` op
JOIN `ecommerce.orders` o ON op.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY 1
ORDER BY total_revenue DESC;
