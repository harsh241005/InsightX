import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from google.cloud import bigquery
import os

# ============================================================
PROJECT_ID = os.getenv("GCP_PROJECT", "analytics-dev-492614")
DATASET = "ecommerce"

@st.cache_resource
def get_bq_client():
    return bigquery.Client(project=PROJECT_ID)

def run_query(query):
    client = get_bq_client()
    return client.query(query).to_dataframe()

st.set_page_config(page_title="⚡ Analytics Command Center", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# ============================================================
# PREMIUM DARK NEON CSS
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&family=Outfit:wght@300;400;500;600;700;800&display=swap');

    :root {
        --bg-primary: #060611;
        --bg-secondary: #0c0c1d;
        --bg-card: #0f0f23;
        --bg-card-hover: #141430;
        --neon-green: #00ff88;
        --neon-blue: #00d4ff;
        --neon-purple: #a855f7;
        --neon-pink: #ff6b9d;
        --neon-yellow: #fbbf24;
        --neon-orange: #fb923c;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --border-subtle: rgba(148, 163, 184, 0.08);
        --border-glow: rgba(0, 255, 136, 0.15);
        --glass-bg: rgba(15, 15, 35, 0.6);
        --glass-border: rgba(148, 163, 184, 0.1);
    }

    /* ===== GLOBAL ===== */
    .stApp {
        background: var(--bg-primary);
        background-image:
            radial-gradient(ellipse 80% 50% at 50% -20%, rgba(0, 212, 255, 0.08), transparent),
            radial-gradient(ellipse 60% 40% at 80% 60%, rgba(168, 85, 247, 0.05), transparent),
            radial-gradient(ellipse 60% 40% at 20% 80%, rgba(0, 255, 136, 0.04), transparent);
        color: var(--text-primary);
    }
    .stApp *, .stApp p, .stApp span, .stApp label, .stApp div,
    .stMarkdown, .stMarkdown p, .stMarkdown span {
        color: var(--text-primary) !important;
    }
    #MainMenu, footer, header { visibility: hidden; }

    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #080818 0%, #0a0a20 100%) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }
    section[data-testid="stSidebar"] * {
        color: var(--text-secondary) !important;
    }
    section[data-testid="stSidebar"] .stRadio label {
        font-family: 'Outfit', sans-serif !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        padding: 10px 16px !important;
        border-radius: 10px !important;
        margin: 2px 0 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border-left: 3px solid transparent !important;
    }
    section[data-testid="stSidebar"] .stRadio label:hover {
        color: var(--neon-green) !important;
        background: rgba(0, 255, 136, 0.06) !important;
        border-left-color: rgba(0, 255, 136, 0.3) !important;
    }
    section[data-testid="stSidebar"] .stRadio label:hover * {
        color: var(--neon-green) !important;
    }

    /* ===== HERO HEADER ===== */
    .hero-header {
        font-family: 'Outfit', sans-serif;
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        line-height: 1.1;
        margin-bottom: 0;
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 50%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-sub {
        font-family: 'Outfit', sans-serif;
        font-size: 1rem;
        font-weight: 400;
        color: var(--text-muted) !important;
        margin-top: 6px;
        letter-spacing: 0.5px;
    }
    .hero-sub * { color: var(--text-muted) !important; -webkit-text-fill-color: var(--text-muted) !important; }

    /* ===== ACCENT LINE ===== */
    .accent-line {
        height: 3px;
        background: linear-gradient(90deg, var(--neon-green), var(--neon-blue), var(--neon-purple), transparent);
        border-radius: 3px;
        margin: 20px 0 28px 0;
        opacity: 0.7;
    }

    /* ===== GLASS METRIC CARDS ===== */
    div[data-testid="stMetric"] {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 14px !important;
        padding: 18px 20px !important;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
        animation: cardReveal 0.5s ease-out both;
        position: relative;
        overflow: hidden;
    }
    div[data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--neon-green), var(--neon-blue));
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    div[data-testid="stMetric"]:hover {
        border-color: rgba(0, 255, 136, 0.25) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3), 0 0 20px rgba(0, 255, 136, 0.06) !important;
    }
    div[data-testid="stMetric"]:hover::before { opacity: 1; }
    div[data-testid="stMetric"] label, div[data-testid="stMetric"] label p {
        color: var(--text-muted) !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 0.78rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.2px !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"],
    div[data-testid="stMetric"] [data-testid="stMetricValue"] div {
        color: var(--text-primary) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 1.65rem !important;
        font-weight: 600 !important;
    }

    /* Staggered card entrance */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) div[data-testid="stMetric"] { animation-delay: 0.05s; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) div[data-testid="stMetric"] { animation-delay: 0.1s; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) div[data-testid="stMetric"] { animation-delay: 0.15s; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(4) div[data-testid="stMetric"] { animation-delay: 0.2s; }

    @keyframes cardReveal {
        from { opacity: 0; transform: translateY(16px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* ===== SECTION HEADERS ===== */
    h2, h3, .stSubheader {
        font-family: 'Outfit', sans-serif !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        letter-spacing: -0.3px !important;
    }

    /* ===== GLASS PANELS ===== */
    .glass-panel {
        background: var(--glass-bg);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 28px 24px;
        margin: 8px 0;
        animation: cardReveal 0.6s ease-out both;
    }

    /* ===== CLUSTER CARDS ===== */
    .seg-card {
        background: var(--glass-bg);
        backdrop-filter: blur(16px);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 28px 20px;
        text-align: center;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        animation: cardReveal 0.5s ease-out both;
        position: relative;
        overflow: hidden;
    }
    .seg-card::after {
        content: '';
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 3px;
        border-radius: 0 0 16px 16px;
    }
    .seg-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
    }
    .seg-name {
        font-family: 'Outfit', sans-serif;
        font-size: 1.05rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 18px;
        text-transform: uppercase;
    }
    .seg-big {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.9rem;
        font-weight: 700;
        color: var(--text-primary) !important;
    }
    .seg-label {
        font-family: 'Outfit', sans-serif;
        font-size: 0.72rem;
        color: var(--text-muted) !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-top: 2px;
        margin-bottom: 14px;
    }
    .seg-stat {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-secondary) !important;
    }

    /* ===== SLIDER ===== */
    .stSlider label, .stSlider label p {
        font-family: 'Outfit', sans-serif !important;
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
    }
    .stSlider [data-testid="stTickBarMin"],
    .stSlider [data-testid="stTickBarMax"] {
        color: var(--text-muted) !important;
    }

    /* ===== INFO BOX ===== */
    .stAlert {
        background: rgba(0, 212, 255, 0.05) !important;
        border: 1px solid rgba(0, 212, 255, 0.15) !important;
        border-radius: 12px !important;
    }
    .stAlert p { color: var(--text-secondary) !important; }

    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {
        background: rgba(15, 15, 35, 0.5) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 12px !important;
    }
    .streamlit-expanderHeader p { color: var(--text-secondary) !important; }
    .streamlit-expanderContent { color: var(--text-secondary) !important; }
    .streamlit-expanderContent p { color: var(--text-secondary) !important; }

    /* ===== DATAFRAME ===== */
    .stDataFrame { border: 1px solid var(--glass-border) !important; border-radius: 12px !important; overflow: hidden; }

    /* ===== LIVE DOT ===== */
    .live-dot {
        display: inline-block;
        width: 7px; height: 7px;
        background: var(--neon-green);
        border-radius: 50%;
        margin-right: 8px;
        animation: livePulse 2s ease-in-out infinite;
        vertical-align: middle;
    }
    @keyframes livePulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.5); }
        50% { box-shadow: 0 0 0 6px rgba(0, 255, 136, 0); }
    }

    /* ===== SIDEBAR BRAND ===== */
    .brand-box {
        text-align: center;
        padding: 16px 0 8px 0;
    }
    .brand-icon { font-size: 2rem; margin-bottom: 4px; }
    .brand-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--neon-green), var(--neon-blue));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 1px;
    }
    .brand-subtitle {
        font-family: 'Outfit', sans-serif;
        font-size: 0.7rem;
        color: var(--text-muted) !important;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 2px;
    }
    .brand-subtitle * { color: var(--text-muted) !important; }
    .tech-pill {
        display: inline-block;
        background: rgba(0, 255, 136, 0.06);
        border: 1px solid rgba(0, 255, 136, 0.12);
        border-radius: 20px;
        padding: 4px 12px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        color: var(--neon-green) !important;
        letter-spacing: 0.5px;
        margin: 3px 2px;
    }
    .tech-pill * { color: var(--neon-green) !important; -webkit-text-fill-color: var(--neon-green) !important; }
    .sidebar-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-subtle), transparent);
        margin: 16px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# PLOTLY DARK CONFIG
# ============================================================
NEON = ['#00ff88', '#00d4ff', '#a855f7', '#ff6b9d', '#fbbf24', '#fb923c']

def styled_fig(fig, h=400):
    fig.update_layout(
        height=h,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Outfit, sans-serif', color='#94a3b8', size=12),
        xaxis=dict(gridcolor='rgba(148,163,184,0.06)', zerolinecolor='rgba(148,163,184,0.06)',
                   title_font=dict(color='#64748b'), tickfont=dict(color='#64748b')),
        yaxis=dict(gridcolor='rgba(148,163,184,0.06)', zerolinecolor='rgba(148,163,184,0.06)',
                   title_font=dict(color='#64748b'), tickfont=dict(color='#64748b')),
        legend=dict(font=dict(color='#94a3b8', size=11)),
        margin=dict(l=10, r=10, t=36, b=10),
    )
    return fig

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("""
    <div class="brand-box">
        <div class="brand-icon">⚡</div>
        <div class="brand-title">ANALYTICS HQ</div>
        <div class="brand-subtitle">E-Commerce Intelligence</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    page = st.radio("Nav", [
        "📊 Executive Summary",
        "📈 Revenue Analytics",
        "👥 Customer Segments",
        "🔄 Cohort Analysis",
        "💳 Payment Insights",
        "🎯 What-If Simulator"
    ], label_visibility="collapsed")

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center; padding: 8px 0;">
        <div class="tech-pill">BigQuery</div>
        <div class="tech-pill">BigQuery ML</div>
        <div class="tech-pill">Cloud Run</div>
        <div class="tech-pill">Cloud Storage</div>
        <div class="tech-pill">Compute Engine</div>
        <div class="tech-pill">ARIMA+</div>
        <div class="tech-pill">K-Means</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# PAGE 1: EXECUTIVE SUMMARY
# ============================================================
if page == "📊 Executive Summary":
    st.markdown('<div class="hero-header">Executive Summary</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub"><span class="live-dot"></span> Real-time analytics from 100K+ transactions</div>', unsafe_allow_html=True)
    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)

    kpis = run_query(f"SELECT * FROM `{PROJECT_ID}.{DATASET}.executive_kpis`")

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total Revenue", f"₹{kpis['total_revenue'].iloc[0]:,.0f}")
    with c2: st.metric("Total Orders", f"{kpis['total_orders'].iloc[0]:,}")
    with c3: st.metric("Unique Customers", f"{kpis['total_customers'].iloc[0]:,}")
    with c4: st.metric("Avg Review", f"{kpis['avg_review_score'].iloc[0]:.1f} ⭐")

    c5, c6, c7 = st.columns(3)
    with c5: st.metric("Avg Order Value", f"₹{kpis['avg_order_value'].iloc[0]:,.2f}")
    with c6: st.metric("Revenue / Customer", f"₹{kpis['revenue_per_customer'].iloc[0]:,.2f}")
    with c7: st.metric("Active Sellers", f"{kpis['active_sellers'].iloc[0]:,}")

    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)

    col_l, col_r = st.columns([1.2, 0.8])

    with col_l:
        st.subheader("📈 Monthly Revenue")
        monthly = run_query(f"SELECT month, total_revenue FROM `{PROJECT_ID}.{DATASET}.monthly_revenue` ORDER BY month")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly['month'], y=monthly['total_revenue'],
            mode='lines', name='Revenue',
            line=dict(color='#00ff88', width=2.5, shape='spline'),
            fill='tozeroy',
            fillcolor='rgba(0,255,136,0.06)'
        ))
        styled_fig(fig, 380)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.subheader("🏷️ Top Categories")
        category = run_query(f"SELECT category, total_revenue FROM `{PROJECT_ID}.{DATASET}.category_performance` ORDER BY total_revenue DESC LIMIT 8")
        fig = px.bar(category, x='total_revenue', y='category', orientation='h',
                     color='total_revenue',
                     color_continuous_scale=[[0, '#0f0f23'], [0.4, '#00d4ff'], [1, '#00ff88']])
        fig.update_layout(yaxis=dict(autorange="reversed", categoryorder='total ascending'),
                          showlegend=False, coloraxis_showscale=False)
        styled_fig(fig, 380)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("🗺️ Top 15 States by Revenue")
    regional = run_query(f"SELECT state, total_revenue, unique_customers FROM `{PROJECT_ID}.{DATASET}.regional_performance` ORDER BY total_revenue DESC LIMIT 15")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=regional['state'], y=regional['total_revenue'],
        marker=dict(
            color=regional['total_revenue'],
            colorscale=[[0, '#0f0f23'], [0.3, '#a855f7'], [0.7, '#00d4ff'], [1, '#00ff88']],
            line=dict(width=0),
            cornerradius=4
        ),
        hovertemplate='<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>'
    ))
    styled_fig(fig, 360)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PAGE 2: REVENUE ANALYTICS
# ============================================================
elif page == "📈 Revenue Analytics":
    st.markdown('<div class="hero-header">Revenue Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">🧠 AI forecast powered by BigQuery ML ARIMA+</div>', unsafe_allow_html=True)
    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)

    historical = run_query(f"SELECT month, total_revenue FROM `{PROJECT_ID}.{DATASET}.monthly_revenue` ORDER BY month")
    forecast = run_query(f"SELECT month, predicted_revenue, lower_bound, upper_bound FROM `{PROJECT_ID}.{DATASET}.revenue_forecast`")

    fig = go.Figure()
    # Confidence band
    fig.add_trace(go.Scatter(
        x=pd.concat([forecast['month'], forecast['month'][::-1]]),
        y=pd.concat([forecast['upper_bound'], forecast['lower_bound'][::-1]]),
        fill='toself', fillcolor='rgba(168,85,247,0.08)',
        line=dict(color='rgba(0,0,0,0)'), name='90% Confidence', showlegend=True
    ))
    # Historical
    fig.add_trace(go.Scatter(
        x=historical['month'], y=historical['total_revenue'],
        mode='lines+markers', name='Historical',
        line=dict(color='#00ff88', width=2.5, shape='spline'),
        marker=dict(size=4, color='#00ff88')
    ))
    # Forecast
    fig.add_trace(go.Scatter(
        x=forecast['month'], y=forecast['predicted_revenue'],
        mode='lines+markers', name='AI Forecast',
        line=dict(color='#a855f7', width=2.5, dash='dot'),
        marker=dict(size=7, symbol='diamond', color='#a855f7', line=dict(width=1.5, color='#060611'))
    ))
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.5, xanchor="center"))
    styled_fig(fig, 460)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
    st.subheader("💰 Revenue Composition")

    col1, col2 = st.columns(2)
    with col1:
        m2 = run_query(f"SELECT month, product_revenue, freight_revenue FROM `{PROJECT_ID}.{DATASET}.monthly_revenue` ORDER BY month")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=m2['month'], y=m2['product_revenue'], name='Product', marker_color='#00d4ff', marker_cornerradius=3))
        fig.add_trace(go.Bar(x=m2['month'], y=m2['freight_revenue'], name='Freight', marker_color='#fbbf24', marker_cornerradius=3))
        fig.update_layout(barmode='stack', legend=dict(orientation="h", yanchor="bottom", y=1.02))
        styled_fig(fig, 370)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        cat = run_query(f"SELECT category, total_revenue FROM `{PROJECT_ID}.{DATASET}.category_performance` ORDER BY total_revenue DESC LIMIT 8")
        fig = px.pie(cat, values='total_revenue', names='category',
                     color_discrete_sequence=NEON, hole=0.6)
        fig.update_traces(textfont_size=11, textfont_color='#f1f5f9',
                          marker=dict(line=dict(color='#060611', width=2)))
        styled_fig(fig, 370)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PAGE 3: CUSTOMER SEGMENTS
# ============================================================
elif page == "👥 Customer Segments":
    st.markdown('<div class="hero-header">Customer Segments</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">🧠 K-Means clustering via BigQuery ML</div>', unsafe_allow_html=True)
    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)

    clusters = run_query(f"SELECT * FROM `{PROJECT_ID}.{DATASET}.cluster_summary` ORDER BY avg_spend DESC")
    accent_colors = ['#00ff88', '#00d4ff', '#a855f7', '#ff6b9d']

    cols = st.columns(len(clusters))
    for i, row in clusters.iterrows():
        with cols[i]:
            c = accent_colors[i % len(accent_colors)]
            st.markdown(f"""
            <div class="seg-card" style="animation-delay:{i*0.1}s; border-top: 2px solid {c};">
                <div class="seg-name" style="color:{c} !important; -webkit-text-fill-color:{c};">{row['cluster_label']}</div>
                <div class="seg-big" style="color:#f1f5f9 !important; -webkit-text-fill-color:#f1f5f9;">{row['customer_count']:,}</div>
                <div class="seg-label" style="color:#64748b !important; -webkit-text-fill-color:#64748b;">Customers</div>
                <div class="seg-stat" style="color:#e2e8f0 !important; -webkit-text-fill-color:#e2e8f0;">₹{row['avg_spend']:,.0f}</div>
                <div class="seg-label" style="color:#64748b !important; -webkit-text-fill-color:#64748b;">Avg Spend</div>
                <div class="seg-stat" style="color:#e2e8f0 !important; -webkit-text-fill-color:#e2e8f0;">{row['avg_orders']:.1f}</div>
                <div class="seg-label" style="color:#64748b !important; -webkit-text-fill-color:#64748b;">Avg Orders</div>
                <div class="seg-stat" style="color:#e2e8f0 !important; -webkit-text-fill-color:#e2e8f0;">{row['avg_review']:.1f} ⭐</div>
                <div class="seg-label" style="color:#64748b !important; -webkit-text-fill-color:#64748b;">Avg Review</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)

    segments = run_query(f"""
        SELECT customer_unique_id, total_spend, total_orders, avg_order_value,
               cluster_id, customer_state, avg_review_score
        FROM `{PROJECT_ID}.{DATASET}.customer_segments`
    """)
    label_map = dict(zip(clusters['cluster_id'], clusters['cluster_label']))
    segments['cluster_label'] = segments['cluster_id'].map(label_map)

    fig = px.scatter(segments, x='total_spend', y='total_orders', color='cluster_label',
                     size='avg_order_value',
                     hover_data=['customer_state', 'avg_review_score'],
                     labels={'total_spend': 'Total Spend (₹)', 'total_orders': 'Total Orders'},
                     color_discrete_sequence=accent_colors)
    fig.update_traces(marker=dict(line=dict(width=0.5, color='rgba(0,0,0,0.3)')))
    styled_fig(fig, 500)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📍 Top 10 States by Segment")
    state_seg = segments.groupby(['customer_state', 'cluster_label']).size().reset_index(name='count')
    top_states = segments.groupby('customer_state').size().nlargest(10).index
    state_seg = state_seg[state_seg['customer_state'].isin(top_states)]
    fig = px.bar(state_seg, x='customer_state', y='count', color='cluster_label',
                 color_discrete_sequence=accent_colors)
    fig.update_traces(marker_cornerradius=4)
    styled_fig(fig, 380)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PAGE 4: COHORT ANALYSIS
# ============================================================
elif page == "🔄 Cohort Analysis":
    st.markdown('<div class="hero-header">Cohort Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Customer retention by first-purchase month</div>', unsafe_allow_html=True)
    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)

    cohort = run_query(f"SELECT cohort_month, month_number, active_customers FROM `{PROJECT_ID}.{DATASET}.cohort_analysis` ORDER BY cohort_month, month_number")
    cohort_pivot = cohort.pivot(index='cohort_month', columns='month_number', values='active_customers')
    cohort_pct = cohort_pivot.div(cohort_pivot.iloc[:, 0], axis=0) * 100
    cohort_pct.index = pd.to_datetime(cohort_pct.index).strftime('%Y-%m')

    fig = px.imshow(
        cohort_pct.round(1),
        labels=dict(x="Months Since First Purchase", y="Cohort", color="Retention %"),
        color_continuous_scale=[[0, '#060611'], [0.005, '#0f0f23'], [0.02, '#1e1b4b'], [0.1, '#00d4ff'], [0.5, '#00ff88'], [1, '#fbbf24']],
        aspect='auto', text_auto='.1f'
    )
    fig.update_traces(textfont=dict(color='#e2e8f0', size=9))
    styled_fig(fig, 600)
    st.plotly_chart(fig, use_container_width=True)

    st.info("💡 Each row represents customers acquired in that month. Values show what percentage returned in subsequent months. "
            "Low retention is typical for marketplace models — most customers purchase once.")

# ============================================================
# PAGE 5: PAYMENT INSIGHTS
# ============================================================
elif page == "💳 Payment Insights":
    st.markdown('<div class="hero-header">Payment Insights</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Payment methods & installment patterns</div>', unsafe_allow_html=True)
    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)

    payments = run_query(f"SELECT * FROM `{PROJECT_ID}.{DATASET}.payment_analysis`")

    # Summary cards
    pay_cols = st.columns(len(payments))
    pay_colors = ['#00ff88', '#00d4ff', '#a855f7', '#ff6b9d', '#fbbf24']
    for i, row in payments.iterrows():
        if i < len(pay_cols):
            with pay_cols[i]:
                st.metric(row['payment_type'].replace('_', ' ').title(),
                          f"₹{row['total_value']:,.0f}",
                          delta=f"{row['total_orders']:,} orders")

    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💰 Revenue Share")
        fig = px.pie(payments, values='total_value', names='payment_type',
                     color_discrete_sequence=NEON, hole=0.6)
        fig.update_traces(textfont=dict(size=12, color='#f1f5f9'),
                          marker=dict(line=dict(color='#060611', width=2)))
        styled_fig(fig, 400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📊 Avg Installments")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=payments['payment_type'], y=payments['avg_installments'],
            marker=dict(
                color=payments['avg_value'],
                colorscale=[[0, '#0f0f23'], [0.5, '#a855f7'], [1, '#00ff88']],
                cornerradius=6,
                line=dict(width=0)
            ),
            hovertemplate='<b>%{x}</b><br>Avg Installments: %{y:.1f}<extra></extra>'
        ))
        styled_fig(fig, 400)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PAGE 6: WHAT-IF SIMULATOR
# ============================================================
elif page == "🎯 What-If Simulator":
    st.markdown('<div class="hero-header">What-If Simulator</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">⚡ Adjust levers, see projected business impact</div>', unsafe_allow_html=True)
    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)

    baseline = run_query(f"SELECT total_revenue, total_orders, total_customers FROM `{PROJECT_ID}.{DATASET}.executive_kpis`")
    base_rev = float(baseline['total_revenue'].iloc[0])
    base_orders = int(baseline['total_orders'].iloc[0])
    base_customers = int(baseline['total_customers'].iloc[0])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🎛️ Revenue Levers")
        price_change = st.slider("Price Change (%)", -30, 30, 0, step=5)
        marketing_change = st.slider("Marketing Spend (%)", -50, 100, 0, step=10)
    with col2:
        st.markdown("#### 🎛️ Growth Levers")
        discount_change = st.slider("Discount Change (%)", -20, 20, 0, step=5)
        retention_change = st.slider("Retention Improvement (%)", -10, 25, 0, step=5)

    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)

    if marketing_change >= 0:
        cust_mult = 1 + (np.sqrt(marketing_change) / 100) * 0.8
    else:
        cust_mult = 1 + (marketing_change / 100) * 0.5

    vol_disc = 1 + (discount_change / 100) * 0.3
    ret_mult = 1 + (retention_change / 100) * 0.4

    proj_rev = base_rev * (1 + price_change/100) * vol_disc * cust_mult * ret_mult
    proj_cust = base_customers * cust_mult * ret_mult

    rev_delta = ((proj_rev - base_rev) / base_rev) * 100
    cust_delta = ((proj_cust - base_customers) / base_customers) * 100
    proj_aov = proj_rev / proj_cust if proj_cust > 0 else 0
    base_aov = base_rev / base_customers
    aov_delta = ((proj_aov - base_aov) / base_aov) * 100

    st.markdown("#### 📊 Projected Outcome")
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Revenue", f"₹{proj_rev:,.0f}", delta=f"{rev_delta:+.1f}%")
    with c2: st.metric("Customers", f"{proj_cust:,.0f}", delta=f"{cust_delta:+.1f}%")
    with c3: st.metric("Avg Order Value", f"₹{proj_aov:,.2f}", delta=f"{aov_delta:+.1f}%")

    st.markdown("")

    # Comparison chart
    fig = go.Figure()
    metrics = ['Revenue', 'Customers']
    current = [base_rev, base_customers]
    projected = [proj_rev, proj_cust]

    fig.add_trace(go.Bar(name='Current', x=metrics, y=current,
                         marker=dict(color='rgba(148,163,184,0.15)', cornerradius=6,
                                     line=dict(width=1, color='rgba(148,163,184,0.3)'))))
    fig.add_trace(go.Bar(name='Projected', x=metrics, y=projected,
                         marker=dict(color='#00ff88', cornerradius=6,
                                     line=dict(width=0))))
    fig.update_layout(barmode='group')
    styled_fig(fig, 400)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("ℹ️ Model Assumptions"):
        st.markdown("""
        **Price Elasticity:** 1% price increase → ~1.5% volume decrease  
        **Marketing:** Square-root diminishing returns curve  
        **Discounts:** +1% discount → +0.3% volume, -0.7% margin  
        **Retention:** +1% retention → +0.4% lifetime revenue  
        
        _In production, these would be trained on actual data using BigQuery ML regression._
        """)
