from pathlib import Path
import json
import pandas as pd
import streamlit as st
import plotly.express as px


# ================= CONFIGURATION =================

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data" / "processed"

st.set_page_config(
    page_title="E-commerce Sales Dashboard",
    page_icon="🛒",
    layout="wide"
)


# ================= CUSTOM CSS =================

st.markdown("""
<style>

    .main {
        background-color: #0e1117;
    }

    div[data-testid="stMetric"] {
        background-color: #1e293b;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #334155;
    }

    div[data-testid="stMetricLabel"] {
        color: #94a3b8;
    }

    div[data-testid="stMetricValue"] {
        color: #38bdf8;
    }

    h1, h2, h3 {
        color: #f8fafc;
    }

</style>
""", unsafe_allow_html=True)


# ================= TITLE =================

st.title("🛒 E-commerce Sales Analytics")

st.caption(
    "Business Intelligence Dashboard | "
    "Olist Brazilian E-commerce Dataset"
)


# ================= LOAD DATA =================

needed = [
    "analysis_orders.csv",
    "category_sales.csv",
    "monthly_sales.csv",
    "state_sales.csv",
    "payment_type_sales.csv",
    "kpi_summary.json"
]

missing = [file for file in needed if not (D / file).exists()]

if missing:
    st.error("Processed data files are missing.")
    st.write(missing)
    st.stop()


orders = pd.read_csv(D / "analysis_orders.csv")
cats = pd.read_csv(D / "category_sales.csv")
states = pd.read_csv(D / "state_sales.csv")
payments = pd.read_csv(D / "payment_type_sales.csv")

with open(D / "kpi_summary.json", encoding="utf-8") as f:
    kpis = json.load(f)


orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"],
    errors="coerce"
)


# ================= SIDEBAR FILTERS =================

st.sidebar.title("🎛️ Dashboard Filters")

lo = orders["order_purchase_timestamp"].min()
hi = orders["order_purchase_timestamp"].max()

filtered = orders.copy()

if pd.notna(lo) and pd.notna(hi):

    date_range = st.sidebar.date_input(
        "Select Purchase Date Range",
        value=(lo.date(), hi.date()),
        min_value=lo.date(),
        max_value=hi.date()
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:

        start = pd.Timestamp(date_range[0])
        end = pd.Timestamp(date_range[1]) + pd.Timedelta(days=1)

        filtered = filtered[
            (filtered["order_purchase_timestamp"] >= start) &
            (filtered["order_purchase_timestamp"] < end)
        ]


if "customer_state" in filtered.columns:

    available_states = sorted(
        filtered["customer_state"].dropna().unique().tolist()
    )

    selected_states = st.sidebar.multiselect(
        "Select Customer State",
        available_states,
        default=available_states
    )

    filtered = filtered[
        filtered["customer_state"].isin(selected_states)
    ]


st.sidebar.markdown("---")
st.sidebar.caption("Data Source: Olist Brazilian Marketplace")


# ================= KPI CALCULATIONS =================

revenue = filtered["item_revenue"].sum()

total_orders = filtered["order_id"].nunique()

aov = revenue / total_orders if total_orders else 0

delivered = (
    filtered["order_status"] == "delivered"
).sum()

delivery_rate = (
    delivered / total_orders * 100
    if total_orders else 0
)

customers = filtered["customer_unique_id"].nunique()


# ================= KPI CARDS =================

st.subheader("📊 Business Overview")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "Total Revenue",
    f"R$ {revenue:,.2f}"
)

c2.metric(
    "Total Orders",
    f"{total_orders:,}"
)

c3.metric(
    "Average Order Value",
    f"R$ {aov:,.2f}"
)

c4.metric(
    "Delivered Rate",
    f"{delivery_rate:.2f}%"
)

c5.metric(
    "Unique Customers",
    f"{customers:,}"
)

st.markdown("---")


# ================= MONTHLY REVENUE =================

st.subheader("📈 Sales Performance")

monthly = (
    filtered.dropna(subset=["order_purchase_timestamp"])
    .assign(
        purchase_month=lambda x:
        x["order_purchase_timestamp"].dt.to_period("M").astype(str)
    )
    .groupby("purchase_month", as_index=False)
    .agg(
        item_revenue=("item_revenue", "sum"),
        orders=("order_id", "nunique")
    )
)

fig_monthly = px.line(
    monthly,
    x="purchase_month",
    y="item_revenue",
    markers=True,
    title="Monthly Revenue Trend",
    labels={
        "purchase_month": "Month",
        "item_revenue": "Revenue (BRL)"
    },
    template="plotly_dark"
)

fig_monthly.update_traces(
    line=dict(width=3),
    marker=dict(size=7)
)

st.plotly_chart(
    fig_monthly,
    use_container_width=True
)

st.markdown("---")


# ================= ORDER ANALYSIS =================

st.subheader("📦 Order Analysis")

left, right = st.columns(2)

with left:

    status = (
        filtered["order_status"]
        .value_counts()
        .rename_axis("status")
        .reset_index(name="orders")
    )

    fig_status = px.pie(
        status,
        names="status",
        values="orders",
        hole=0.5,
        title="Order Status Distribution",
        template="plotly_dark"
    )

    st.plotly_chart(
        fig_status,
        use_container_width=True
    )


# ================= CATEGORY ANALYSIS =================

cats["display_category"] = (
    cats["category"]
    .fillna("Unknown")
    .str.replace("_", " ")
    .str.title()
)

top_categories = (
    cats.nlargest(10, "item_revenue")
    .sort_values("item_revenue")
)

with right:

    fig_category = px.bar(
        top_categories,
        x="item_revenue",
        y="display_category",
        orientation="h",
        title="Top 10 Product Categories",
        labels={
            "item_revenue": "Revenue (BRL)",
            "display_category": "Category"
        },
        template="plotly_dark"
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True
    )


st.markdown("---")


# ================= STATE ANALYSIS =================

st.subheader("🌎 Geographic Sales Analysis")

state_sales = (
    filtered.groupby("customer_state", as_index=False)
    .agg(
        item_revenue=("item_revenue", "sum"),
        orders=("order_id", "nunique")
    )
    .sort_values("item_revenue", ascending=False)
)

left, right = st.columns(2)

with left:

    top_states = (
        state_sales.nlargest(10, "item_revenue")
        .sort_values("item_revenue")
    )

    fig_state = px.bar(
        top_states,
        x="item_revenue",
        y="customer_state",
        orientation="h",
        title="Top 10 Customer States",
        labels={
            "item_revenue": "Revenue (BRL)",
            "customer_state": "State"
        },
        template="plotly_dark"
    )

    st.plotly_chart(
        fig_state,
        use_container_width=True
    )


with right:

    st.subheader("State-wise Sales Table")

    st.dataframe(
        state_sales.head(10),
        use_container_width=True,
        hide_index=True
    )


# ================= PAYMENT ANALYSIS =================

st.markdown("---")

st.subheader("💳 Payment Analysis")

fig_payment = px.bar(
    payments,
    x="payment_type",
    y="payment_value",
    text_auto=".2s",
    title="Payment Value by Payment Method",
    labels={
        "payment_type": "Payment Method",
        "payment_value": "Payment Value (BRL)"
    },
    template="plotly_dark"
)

st.plotly_chart(
    fig_payment,
    use_container_width=True
)


# ================= BUSINESS INSIGHTS =================

st.markdown("---")

st.subheader("💡 Business Insights")

i1, i2, i3 = st.columns(3)

if not state_sales.empty:

    best_state = state_sales.iloc[0]["customer_state"]

    i1.info(
        f"🏆 Highest Revenue State: **{best_state}**"
    )

else:
    i1.info("No state data available.")


if not cats.empty:

    best_category = cats.loc[
        cats["item_revenue"].idxmax(),
        "display_category"
    ]

    i2.info(
        f"🛍️ Top Product Category: **{best_category}**"
    )

else:
    i2.info("No category data available.")


i3.info(
    f"📦 Delivered Orders: **{delivered:,}**"
)


# ================= DOWNLOAD DATA =================

st.markdown("---")

st.subheader("📥 Download Data")

csv = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Orders CSV",
    data=csv,
    file_name="filtered_ecommerce_orders.csv",
    mime="text/csv"
)


# ================= DATA TABLE =================

with st.expander("View Detailed Order Records"):

    st.dataframe(
        filtered.head(500),
        use_container_width=True,
        hide_index=True
    )


# ================= FOOTER =================

st.markdown("---")

st.caption(
    "E-commerce Sales Analytics | "
    "Built with Python, Pandas, Plotly and Streamlit"
)

st.caption(
    "Dataset: Olist Brazilian E-commerce | "
    "Currency: Brazilian Real (BRL)"
)

st.caption(
    "Revenue represents item prices excluding freight. "
    "Category and payment charts show full-period summaries."
)