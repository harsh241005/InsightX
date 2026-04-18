-- ============================================================
-- InsightX — BigQuery ML Model Training
-- Run these in BigQuery Console
-- ============================================================

-- MODEL 1: ARIMA+ Revenue Forecasting
-- Trains on monthly revenue data and learns trend + seasonality
CREATE OR REPLACE MODEL `ecommerce.revenue_forecast_model`
OPTIONS(
    model_type = 'ARIMA_PLUS',
    time_series_timestamp_col = 'month',
    time_series_data_col = 'total_revenue',
    auto_arima = TRUE,
    data_frequency = 'MONTHLY'
) AS
SELECT month, total_revenue
FROM `ecommerce.monthly_revenue`
ORDER BY month;

-- Generate 6-month forecast with confidence intervals
CREATE OR REPLACE TABLE `ecommerce.revenue_forecast` AS
SELECT *
FROM ML.FORECAST(MODEL `ecommerce.revenue_forecast_model`,
    STRUCT(6 AS horizon, 0.9 AS confidence_level));

-- MODEL 2: K-Means Customer Segmentation
-- Clusters customers into 4 segments based on purchasing behavior
CREATE OR REPLACE MODEL `ecommerce.customer_segments_model`
OPTIONS(
    model_type = 'KMEANS',
    num_clusters = 4,
    standardize_features = TRUE
) AS
SELECT
    total_spend,
    total_orders,
    avg_order_value,
    active_months,
    avg_review_score
FROM `ecommerce.customer_metrics`
WHERE total_spend > 0;

-- Generate segment assignments
CREATE OR REPLACE TABLE `ecommerce.customer_segments` AS
SELECT
    cm.*,
    pred.CENTROID_ID as segment_id,
    CASE pred.CENTROID_ID
        WHEN 1 THEN 'Champions'
        WHEN 2 THEN 'High Value'
        WHEN 3 THEN 'Growing Regulars'
        WHEN 4 THEN 'Casual Buyers'
    END as segment_label
FROM ML.PREDICT(MODEL `ecommerce.customer_segments_model`,
    (SELECT * FROM `ecommerce.customer_metrics` WHERE total_spend > 0)
) pred
JOIN `ecommerce.customer_metrics` cm
ON pred.customer_unique_id = cm.customer_unique_id;
