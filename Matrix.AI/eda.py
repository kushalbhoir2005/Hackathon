import pandas as pd
import numpy as np
import os

# =========================
# LOAD DATA
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "store_sales.csv")

df = pd.read_csv(file_path)

# =========================
# CORE CALCULATIONS
# =========================

def process_data():

    # KPIs
    total_revenue = df["Amount"].sum()
    total_orders = len(df)
    avg_order = total_revenue / total_orders
    avg_rating = df["ItemRating"].mean()
    popular_product = df["ItemPurchased"].value_counts().idxmax()
    repeat_rate = (df[df["PreviousPurchases"] > 1].shape[0] / len(df)) * 100

    top_category = (
        df.groupby("Category")["Amount"]
        .sum()
        .idxmax()
    )

    # ----------------------
    # DEMAND + INVENTORY
    # ----------------------
    df["quantity"] = (df["Amount"] / df["Amount"].median()).clip(1,5).astype(int)

    df["inventory"] = (
        df["quantity"] * np.random.uniform(0.6,1.2,len(df))
    ).astype(int)

    df["stockout"] = (df["inventory"] < df["quantity"]).astype(int)

    df["lost_revenue_row"] = np.where(
        df["stockout"] == 1,
        df["Amount"] * 0.3,
        0
    )

    stockout_count = df["stockout"].sum()
    lost_revenue = df["lost_revenue_row"].sum()

    # ----------------------
    # PROFIT CALCULATION 🔥
    # ----------------------
    cost = total_revenue * 0.7
    profit = total_revenue - cost - lost_revenue

    # ----------------------
    # TREND
    # ----------------------
    df["date"] = pd.date_range(start="2023-01-01", periods=len(df), freq="H")

    monthly = df.groupby(df["date"].dt.to_period("M"))["Amount"].sum()

    labels = monthly.index.astype(str).tolist()
    revenue = monthly.values.tolist()

    ma3 = pd.Series(revenue).rolling(3, min_periods=1).mean().tolist()

    # =========================
    # ✅ NEW: CATEGORY + TOP 5
    # =========================
    category_group = df.groupby("Category")["Amount"].sum().reset_index()

    category_data = {
        "labels": category_group["Category"].tolist(),
        "values": category_group["Amount"].tolist()
    }

    top5 = category_group.sort_values(by="Amount", ascending=False).head(5)

    top5_data = {
        "labels": top5["Category"].tolist(),
        "values": top5["Amount"].tolist()
    }

    return {
        "kpis": {
            "total_revenue": f"₹{total_revenue:,.0f}",
            "avg_order": f"₹{avg_order:,.0f}",
            "total_orders": f"{total_orders:,}",
            "stockout_count": int(stockout_count),
            "lost_revenue": f"₹{lost_revenue:,.0f}",
            "profit": f"₹{profit:,.0f}",
            "top_category": top_category,
            "avg_rating": round(avg_rating, 2),
            "repeat_rate": f"{round(repeat_rate,1)}%",
            "popular_product": popular_product,
        },
        "trends": {
            "labels": labels,
            "revenue": revenue,
            "ma3": ma3
        },
        "anomalies": {
            "count": int(len(df) * 0.05)
        },

        # ✅ ADDED ONLY
        "category": category_data,
        "top5": top5_data
    }

# =========================
# MAIN FUNCTION
# =========================

def get_dashboard_data():
    return process_data()