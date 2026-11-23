from pathlib import Path
import sqlite3
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/"data/raw"
DB=ROOT/"data/processed/olist_sales.db"
TABLES={"orders":"olist_orders_dataset.csv","order_items":"olist_order_items_dataset.csv",
"products":"olist_products_dataset.csv","customers":"olist_customers_dataset.csv",
"payments":"olist_order_payments_dataset.csv",
"category_translation":"product_category_name_translation.csv"}

def main():
    DB.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(DB) as conn:
        for table,file in TABLES.items():
            path=RAW/file
            if path.exists():
                df=pd.read_csv(path)
                df.to_sql(table,conn,if_exists="replace",index=False)
                print(f"{table}: {len(df):,} rows")
            else:
                print(f"Skipped missing {file}")
    print("SQLite database:",DB)

if __name__=="__main__":
    main()
