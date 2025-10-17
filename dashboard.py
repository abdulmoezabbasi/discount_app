# ================================================
# 🛍️ DISCOUNT ANALYSIS - ECOMMERCE DASHBOARD
# ================================================
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import os

# -----------------------------
# PAGE CONFIGURATION
# -----------------------------
st.set_page_config(
    page_title="E-Commerce Discount Analysis",
    page_icon="💸",
    layout="wide"
)

st.title("📊 E-Commerce Discount Analysis Dashboard")
st.markdown("Analyze how discounts affect **sales, profit, and customer behavior** across categories and regions.")

# -----------------------------
# LOAD DATA FROM LOCAL FILE
# -----------------------------
file_path = "ecommerce_dataset.csv"  # 👈 Your dataset is in same folder

if not os.path.exists(file_path):
    st.error("❌ Dataset not found. Make sure 'ecommerce_dataset.csv' is in the same folder as this file.")
    st.stop()

@st.cache_data
def load_data():
    df = pd.read_csv(file_path)
    return df

df = load_data()

# -----------------------------
# DATA CLEANING & PREPARATION
# -----------------------------
if "order_date" in df.columns:
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

# Standardize column names (in case of case differences)
df.columns = [col.strip().lower() for col in df.columns]

# Feature engineering
df["revenue"] = df["price"] * df["quantity"]
df["discount_value"] = df["revenue"] * df["discount"]
df["profit"] = df["revenue"] - df["discount_value"]
df["profit_margin"] = df["profit"] / df["revenue"]

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("🔍 Filters")

categories = st.sidebar.multiselect(
    "Select Categories:",
    options=df["category"].unique(),
    default=df["category"].unique()
)

regions = st.sidebar.multiselect(
    "Select Regions:",
    options=df["region"].unique(),
    default=df["region"].unique()
)

discount_range = st.sidebar.slider(
    "Select Discount Range:",
    float(df["discount"].min()), 
    float(df["discount"].max()), 
    (float(df["discount"].min()), float(df["discount"].max()))
)

filtered_df = df[
    (df["category"].isin(categories)) &
    (df["region"].isin(regions)) &
    (df["discount"] >= discount_range[0]) &
    (df["discount"] <= discount_range[1])
]

# -----------------------------
# KPI METRICS
# -----------------------------
st.markdown("### 📈 Key Metrics")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Average Discount", f"{filtered_df['discount'].mean():.2%}")
col2.metric("Total Revenue", f"${filtered_df['revenue'].sum():,.0f}")
col3.metric("Total Profit", f"${filtered_df['profit'].sum():,.0f}")
col4.metric("Avg Profit Margin", f"{filtered_df['profit_margin'].mean():.1%}")

# -----------------------------
# MAIN VISUALS
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "💸 Discount Impact", "🌍 Regional Analysis", "🔍 Correlations"])

# ---- Overview
with tab1:
    st.subheader("Dataset Preview")
    st.dataframe(filtered_df.head(10))

    st.subheader("Discount Distribution")
    fig = px.histogram(filtered_df, x="discount", nbins=25, color="category", title="Discount Distribution by Category")
    st.plotly_chart(fig, use_container_width=True)

# ---- Discount Impact
with tab2:
    st.subheader("Discount vs Revenue")
    fig = px.scatter(filtered_df, x="discount", y="revenue", color="category", opacity=0.7, title="Revenue vs Discount")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Discount vs Profit")
    fig = px.scatter(filtered_df, x="discount", y="profit", color="region", opacity=0.7, title="Profit vs Discount")
    st.plotly_chart(fig, use_container_width=True)

# ---- Regional
with tab3:
    st.subheader("Discount Patterns Across Regions")
    fig = px.box(filtered_df, x="region", y="discount", color="region", title="Discount Patterns by Region")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Average Profit by Category (Discounted vs Non-Discounted)")
    profit_cat = (
        filtered_df.groupby(["category", filtered_df["discount"] > 0])["profit"]
        .mean()
        .reset_index()
    )
    profit_cat["Discounted"] = profit_cat["discount"].map({True: "Discounted", False: "Non-Discounted"})

    fig = px.bar(profit_cat, x="category", y="profit", color="Discounted", barmode="group", title="Profit by Category")
    st.plotly_chart(fig, use_container_width=True)

# ---- Correlations
with tab4:
    st.subheader("Correlation Heatmap")
    corr_cols = ["discount", "revenue", "profit", "quantity"]
    corr = filtered_df[corr_cols].corr()
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

# -----------------------------
# INSIGHTS
# -----------------------------
st.header("💡 Key Insights")

discounted = filtered_df[filtered_df["discount"] > 0]
non_discounted = filtered_df[filtered_df["discount"] == 0]

if not non_discounted.empty:
    sales_boost = ((discounted["quantity"].mean() - non_discounted["quantity"].mean()) / non_discounted["quantity"].mean()) * 100
    profit_diff = ((discounted["profit_margin"].mean() - non_discounted["profit_margin"].mean()) * 100)

    st.success(f"💹 Discounts increase average quantity sold by **{sales_boost:.1f}%** on average.")
    st.warning(f"💰 Profit margins shrink by about **{profit_diff:.1f} percentage points** when discounts are applied.")
else:
    st.info("⚠️ All items have discounts — cannot compare with non-discounted sales.")

st.info("📆 Seasonal trends may show higher discounts during sales months or special events.")
st.info("🏷️ Electronics and Sports typically benefit most from well-calibrated discounts.")
st.balloons()
