# E-commerce Sales Analysis & Business Intelligence

End-to-end DSV portfolio project using the Brazilian E-Commerce Public Dataset by Olist. Includes Python data cleaning, EDA, KPIs, visualizations, SQLite loading, SQL business queries, and an interactive Streamlit dashboard.

## Dataset
Download the Olist dataset: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
Extract these CSVs into `data/raw/`:
- olist_orders_dataset.csv
- olist_order_items_dataset.csv
- olist_products_dataset.csv
- olist_customers_dataset.csv
- olist_order_payments_dataset.csv
- product_category_name_translation.csv

Optional source files: sellers, reviews, geolocation. Dataset is not bundled because it is large and distributed by Kaggle.

## Setup (Windows / VS Code)
```bash
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
Run:
```bash
python src/analyze.py
python src/load_sqlite.py
streamlit run dashboard/app.py
```

## Project contents
- `src/analyze.py`: cleaning, merging, KPI calculation, EDA summaries and charts.
- `src/load_sqlite.py`: loads source tables into SQLite.
- `sql/analysis.sql`: business queries.
- `dashboard/app.py`: interactive dashboard.
- `power_bi/POWER_BI_GUIDE.md`: Power BI model, DAX measures and layout.

## Metrics
Revenue means sum of item prices (freight excluded). AOV = item revenue / distinct orders. Delivered rate = delivered orders / all orders in the selected set. Use distinct order counts to avoid double counting.

## Outputs
Processed CSVs and KPI JSON are written to `data/processed/`; charts go to `reports/figures/`.

## Resume wording (only after running and verifying)
**E-commerce Sales Analysis & Business Intelligence Dashboard**
- Analyzed Olist marketplace transactions using Python, Pandas and SQL to explore sales, category, regional, payment and delivery trends.
- Built an interactive dashboard with revenue, order, average order value and delivery KPIs.
- Performed data cleaning and exploratory analysis and created business-focused visualizations.
Add numerical results only after calculating them from your own run.

## Limitations
This historical dataset represents a Brazilian marketplace. It is observational data and does not establish causation. Product revenue in this project excludes freight unless explicitly stated.
