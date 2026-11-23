from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
RAW, OUT, FIG = ROOT/"data/raw", ROOT/"data/processed", ROOT/"reports/figures"
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

def load(name):
    p = RAW/name
    if not p.exists():
        raise FileNotFoundError(f"Missing {name}. Download Olist CSVs into {RAW}")
    return pd.read_csv(p)

def main():
    orders = load("olist_orders_dataset.csv")
    items = load("olist_order_items_dataset.csv")
    products = load("olist_products_dataset.csv")
    customers = load("olist_customers_dataset.csv")
    payments = load("olist_order_payments_dataset.csv")
    trans = load("product_category_name_translation.csv")

    for c in ["order_purchase_timestamp","order_approved_at",
              "order_delivered_customer_date","order_estimated_delivery_date"]:
        orders[c] = pd.to_datetime(orders[c], errors="coerce")

    products = products.merge(trans, on="product_category_name", how="left")
    products["category"] = products["product_category_name_english"].fillna(
        products["product_category_name"]).fillna("unknown")

    detail = items.merge(products[["product_id","category"]], on="product_id", how="left")
    detail["category"] = detail["category"].fillna("unknown")
    detail["price"] = pd.to_numeric(detail["price"], errors="coerce").fillna(0)
    detail["freight_value"] = pd.to_numeric(detail["freight_value"], errors="coerce").fillna(0)

    oi = detail.groupby("order_id", as_index=False).agg(
        item_revenue=("price","sum"), freight_value=("freight_value","sum"),
        item_count=("order_item_id","count"))
    pay = payments.groupby("order_id", as_index=False).agg(
        payment_value=("payment_value","sum"))
    cust = customers[["customer_id","customer_unique_id","customer_state","customer_city"]]
    data = orders.merge(oi,on="order_id",how="left").merge(pay,on="order_id",how="left").merge(
        cust,on="customer_id",how="left")
    for c in ["item_revenue","freight_value","item_count","payment_value"]:
        data[c] = data[c].fillna(0)
    data["purchase_month"] = data["order_purchase_timestamp"].dt.to_period("M").astype("string")
    data["delivery_days"] = (data["order_delivered_customer_date"]-
                             data["order_purchase_timestamp"]).dt.total_seconds()/86400
    data["delivery_delay_days"] = (data["order_delivered_customer_date"]-
                                   data["order_estimated_delivery_date"]).dt.total_seconds()/86400
    data.to_csv(OUT/"analysis_orders.csv",index=False)

    category = detail.groupby("category",as_index=False).agg(
        item_revenue=("price","sum"),freight_value=("freight_value","sum"),
        units=("order_item_id","count"),orders=("order_id","nunique")
    ).sort_values("item_revenue",ascending=False)
    category.to_csv(OUT/"category_sales.csv",index=False)

    monthly = data.dropna(subset=["purchase_month"]).groupby("purchase_month",as_index=False).agg(
        item_revenue=("item_revenue","sum"),orders=("order_id","nunique"))
    monthly.to_csv(OUT/"monthly_sales.csv",index=False)

    state = data.groupby("customer_state",as_index=False).agg(
        item_revenue=("item_revenue","sum"),orders=("order_id","nunique"),
        customers=("customer_unique_id","nunique")).sort_values("item_revenue",ascending=False)
    state.to_csv(OUT/"state_sales.csv",index=False)

    ptype = payments.groupby("payment_type",as_index=False).agg(
        payment_value=("payment_value","sum"),payment_records=("payment_type","size"))
    ptype.to_csv(OUT/"payment_type_sales.csv",index=False)

    norders = int(data.order_id.nunique())
    delivered = int((data.order_status=="delivered").sum())
    revenue = float(data.item_revenue.sum())
    kpis = {"total_item_revenue":revenue,"total_orders":norders,
            "average_order_value":revenue/norders if norders else 0,
            "delivered_orders":delivered,
            "delivered_rate_pct":100*delivered/norders if norders else 0,
            "total_freight_value":float(data.freight_value.sum()),
            "unique_customers":int(data.customer_unique_id.nunique())}
    (OUT/"kpi_summary.json").write_text(json.dumps(kpis,indent=2),encoding="utf-8")

    sns.set_theme(style="whitegrid")
    plots = [
        (monthly,"purchase_month","item_revenue","Monthly Item Revenue","monthly_revenue.png","line"),
        (category.head(12).sort_values("item_revenue"),"item_revenue","category","Top Categories by Item Revenue","top_categories.png","barh"),
        (state.head(12).sort_values("item_revenue"),"item_revenue","customer_state","Top Customer States by Revenue","top_states.png","barh"),
        (ptype,"payment_type","payment_value","Payment Value by Type","payment_types.png","bar"),
    ]
    for df,x,y,title,filename,kind in plots:
        plt.figure(figsize=(11,5))
        if kind=="line":
            sns.lineplot(data=df,x=x,y=y,marker="o")
            plt.xticks(rotation=60,ha="right")
        elif kind=="barh":
            sns.barplot(data=df,x=x,y=y)
        else:
            sns.barplot(data=df,x=x,y=y)
            plt.xticks(rotation=25)
        plt.title(title); plt.tight_layout(); plt.savefig(FIG/filename,dpi=150); plt.close()
    print("Analysis complete. KPI summary:")
    print(json.dumps(kpis,indent=2))

if __name__=="__main__":
    main()
