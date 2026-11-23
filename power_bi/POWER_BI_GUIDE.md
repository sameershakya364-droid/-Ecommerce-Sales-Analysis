# Power BI Dashboard Guide

## Import
Run `python src/analyze.py`, then import `analysis_orders.csv`, `category_sales.csv`,
`monthly_sales.csv`, `state_sales.csv`, and `payment_type_sales.csv` from `data/processed/`.

For a relational model, import the original Olist CSVs and create:
- customers[customer_id] 1:* orders[customer_id]
- orders[order_id] 1:* order_items[order_id]
- products[product_id] 1:* order_items[product_id]
- orders[order_id] 1:* payments[order_id]

Do not flatten order items and payment rows together without aggregation; multiple items and payments can multiply totals.

## DAX measures
```DAX
Total Item Revenue = SUM(order_items[price])
Total Freight = SUM(order_items[freight_value])
Total Orders = DISTINCTCOUNT(orders[order_id])
Average Order Value = DIVIDE([Total Item Revenue], [Total Orders])
Delivered Orders =
CALCULATE(DISTINCTCOUNT(orders[order_id]), orders[order_status] = "delivered")
Delivered Rate = DIVIDE([Delivered Orders], [Total Orders])
```
Format Delivered Rate as percentage. Revenue is item price only, freight excluded.

## Suggested one-page layout
- KPI cards: Item Revenue, Orders, AOV, Delivered Rate
- Line chart: Monthly item revenue
- Bar chart: Revenue by product category
- Bar/map: Orders or revenue by customer state
- Donut: Order status
- Bar chart: Payment type
- Slicers: Purchase date, customer state, order status, category

Validate dashboard totals against `kpi_summary.json` and processed CSVs.
