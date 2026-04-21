# InsightX — E-Commerce Analytics Platform on Google Cloud

> An end-to-end intelligent analytics platform that processes 100K+ real-world e-commerce transactions, applies ML models for revenue forecasting and customer segmentation, and serves insights through an interactive dashboard deployed on Google Cloud.

**Live Dashboard:** [https://analytics-dashboard-169375435948.asia-south1.run.app](https://analytics-dashboard-169375435948.asia-south1.run.app)

**Dashboard Image** 
<img width="1891" height="888" alt="image" src="https://github.com/user-attachments/assets/2cace6ca-06d5-4a14-854d-5603e6f91001" />


---

## What It Does

InsightX takes raw e-commerce data from the [Olist Brazilian Marketplace](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) and transforms it into actionable business intelligence through a fully cloud-native pipeline:

| Stage | What Happens | GCP Service |
|-------|-------------|-------------|
| **Ingest** | 9 CSV files (100K+ orders) uploaded to cloud storage | Cloud Storage |
| **Warehouse** | Raw data loaded and transformed into 7 analytics tables | BigQuery |
| **Model** | ARIMA+ revenue forecast + K-Means customer segmentation trained in SQL | BigQuery ML |
| **Serve** | 6-page interactive Streamlit dashboard with dark neon theme | Cloud Run |
| **Build** | Dockerized app built and deployed via CI pipeline | Cloud Build |
| **Develop** | All development done on a cloud VM | Compute Engine |

## Key Business Insights

- **₹15.5M total revenue** from 96K+ delivered orders across Brazil
- **Credit card installment purchases drive 74% of revenue** — average 3-4 installments per order
- **Single-purchase customers dominate** — most customers buy only once (typical marketplace pattern)
- **São Paulo generates 40%+ of all revenue** — massive geographic concentration
- **Revenue forecast** shows continued growth with seasonal patterns identified by ARIMA+

## Dashboard Pages

### 1. Executive Summary
Headline KPIs (revenue, orders, customers, sellers, avg order value, review score) with monthly trend charts and year-over-year comparisons.

### 2. Revenue Analytics
Monthly revenue time series with AI-generated 6-month ARIMA+ forecast including 90% confidence intervals.

### 3. Customer Segments
Interactive scatter plot of 4 ML-identified customer clusters (Champions, High Value, Growing Regulars, Casual Buyers) based on spending behavior, with segment-level statistics.

### 4. Cohort Analysis
Customer retention heatmap grouped by first-purchase month, showing how many customers return in subsequent months.

### 5. Payment Insights
Revenue breakdown by payment method (credit card, boleto, voucher, debit) with installment pattern analysis.

### 6. What-If Simulator
Interactive business simulation tool with 4 sliders (price change, marketing spend, discount rate, retention improvement) that projects the impact on revenue, customers, and average order value using economic elasticity models.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Kaggle     │────▶│ Cloud Storage │────▶│  BigQuery    │
│  (9 CSVs)    │     │  (Data Lake)  │     │ (Warehouse)  │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                │
                                    ┌───────────┴───────────┐
                                    │                       │
                              ┌─────▼─────┐          ┌─────▼─────┐
                              │ BigQuery   │          │ Analytics  │
                              │ ML Models  │          │  Tables    │
                              │ (ARIMA+,   │          │ (7 tables) │
                              │  K-Means)  │          └─────┬─────┘
                              └─────┬─────┘                │
                                    │                       │
                                    └───────────┬───────────┘
                                                │
                                          ┌─────▼─────┐
                                          │ Streamlit  │
                                          │ Dashboard  │
                                          │ (6 pages)  │
                                          └─────┬─────┘
                                                │
                                    ┌───────────┴───────────┐
                                    │                       │
                              ┌─────▼─────┐          ┌─────▼─────┐
                              │  Docker    │          │ Cloud Run  │
                              │ Container  │────────▶ │ (Live URL) │
                              │(Cloud Build)│         └───────────┘
                              └───────────┘
```

## Tech Stack

| Category | Tools |
|----------|-------|
| **Language** | Python 3.10, SQL |
| **Dashboard** | Streamlit 1.56, Plotly 5.18 |
| **Data** | Pandas, NumPy, PyArrow |
| **ML Models** | BigQuery ML (ARIMA+, K-Means) |
| **Cloud** | GCP — Compute Engine, Cloud Storage, BigQuery, Cloud Build, Cloud Run |
| **Deployment** | Docker, gcloud CLI |
| **Design** | Dark neon theme, glassmorphism, Outfit + JetBrains Mono fonts |

## Project Structure

```
InsightX/
├── app.py                    # Main Streamlit dashboard (6 pages)
├── Dockerfile                # Container config for Cloud Run
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── config.toml           # Streamlit dark theme config
├── sql/
│   ├── 01_analytics_tables.sql   # 7 BigQuery analytics table queries
│   └── 02_bigquery_ml.sql        # ARIMA+ and K-Means model training
├── docs/
│   └── architecture.md       # Detailed architecture notes
└── README.md
```

## How to Reproduce

### Prerequisites
- Google Cloud account with billing enabled
- `gcloud` CLI installed
- Python 3.10+

### Step 1: GCP Setup
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable bigquery.googleapis.com storage.googleapis.com run.googleapis.com cloudbuild.googleapis.com
```

### Step 2: Data Pipeline
1. Download the [Olist dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) from Kaggle
2. Upload CSVs to Cloud Storage: `gsutil cp *.csv gs://YOUR_BUCKET/raw/`
3. Load into BigQuery via Console (auto-detect schema)
4. Run queries in `sql/01_analytics_tables.sql` to create analytics tables
5. Run queries in `sql/02_bigquery_ml.sql` to train ML models

### Step 3: Run Locally
```bash
pip install -r requirements.txt
export GCP_PROJECT=YOUR_PROJECT_ID
streamlit run app.py
```

### Step 4: Deploy to Cloud Run
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/analytics-dashboard --timeout=900
gcloud run deploy analytics-dashboard \
    --image gcr.io/YOUR_PROJECT_ID/analytics-dashboard \
    --platform managed \
    --region asia-south1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --set-env-vars GCP_PROJECT=YOUR_PROJECT_ID
```

## Dataset

**Source:** [Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (Kaggle)

| Table | Records | Description |
|-------|---------|-------------|
| orders | ~100K | Order metadata and timestamps |
| order_items | ~112K | Line items with price and freight |
| customers | ~99K | Customer demographics and location |
| products | ~32K | Product catalog and dimensions |
| order_reviews | ~100K | Customer review scores and comments |
| order_payments | ~103K | Payment type and installments |
| sellers | ~3K | Seller information |
| geolocation | ~1M | Latitude/longitude data |
| category_translation | 71 | Portuguese to English category names |

## Author

**Harsh Palyekar** — B.Sc. Data Science, Goa University
[LinkedIn](https://www.linkedin.com/in/harsh-palyekar-790209295) · [GitHub](https://github.com/harsh241005)
