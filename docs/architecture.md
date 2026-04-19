# InsightX — Architecture Notes

## GCP Services Used (6)

1. **Compute Engine** — e2-medium VM (2 vCPU, 4GB RAM), Ubuntu 22.04, asia-south1 (Mumbai). Used as the development environment.
2. **Cloud Storage** — Standard storage bucket for raw CSV files (~120MB). Bucket: `analytics-dev-492614-analytics-data`
3. **BigQuery** — Serverless data warehouse. Dataset: `ecommerce` with 16+ tables (9 raw + 7 analytics + ML outputs)
4. **BigQuery ML** — Trained ARIMA+ (revenue forecasting) and K-Means (customer segmentation) models using SQL
5. **Cloud Build** — Built Docker container image from Dockerfile and pushed to Artifact Registry
6. **Cloud Run** — Hosted the Streamlit dashboard as a serverless container. Region: asia-south1

## Data Pipeline Flow

1. Download Olist dataset from Kaggle (9 CSV files)
2. Upload to Cloud Storage bucket under `raw/` prefix
3. Load each CSV into BigQuery via Console UI (auto-detect schema)
4. Run SQL transformations to create 7 analytics tables
5. Train 2 ML models in BigQuery ML
6. Streamlit app queries BigQuery directly for live data
7. App containerized with Docker and deployed to Cloud Run

## ML Models

### ARIMA+ Revenue Forecast
- Trained on monthly_revenue table
- Auto-detects trend and seasonality
- Generates 6-month forecast with 90% confidence intervals

### K-Means Customer Segmentation
- Features: total_spend, total_orders, avg_order_value, active_months, avg_review_score
- 4 clusters: Champions, High Value, Growing Regulars, Casual Buyers
- Standardized features before clustering

## Dataset Statistics
- Total Revenue: ₹15,489,666
- Total Delivered Orders: 96,478
- Unique Customers: 96,478
- Active Sellers: 2,970
- Average Order Value: ₹139.75
- Average Review Score: 4.1/5
