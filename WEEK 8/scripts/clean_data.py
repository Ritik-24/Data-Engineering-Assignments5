import os
import pandas as pd
import numpy as np

# Setup directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
CLEANED_DIR = os.path.join(BASE_DIR, "data", "cleaned")
os.makedirs(CLEANED_DIR, exist_ok=True)

def apply_clean(file_name, id_col, clean_func=None):
    """Utility to load, deduplicate, and perform specific cleaning logic."""
    print(f"\nProcessing {file_name}...")
    df = pd.read_csv(os.path.join(RAW_DIR, file_name))
    
    # 1. Structural Cleaning: Force ID to string and drop duplicates
    df[id_col] = df[id_col].astype(str).str.strip()
    initial_len = len(df)
    df = df.drop_duplicates(subset=[id_col], keep='first')
    print(f"  Dropped {initial_len - len(df)} duplicates.")
    print(f"  Final row count: {len(df)}")
    
    # 2. Content Cleaning: Apply custom logic (dates, names, NULLs)
    if clean_func:
        df = clean_func(df)
        
    df.to_csv(os.path.join(CLEANED_DIR, file_name.replace(".csv", "_clean.csv")), index=False)
    return df

def clean_customers():
    def logic(df):
        # Requirement: Fill missing emails
        df['email'] = df['email'].fillna('unknown@example.com')
        return df
    return apply_clean("customers.csv", "customer_id", logic)

def clean_products():
    def logic(df):
        # Requirement: Normalize product names (trim, title case)
        df['product_name'] = df['product_name'].astype(str).str.strip().str.title()
        return df
    return apply_clean("products.csv", "product_id", logic)

def clean_orders():
    def logic(df):
        # Requirement: Fix date formats and handle NULL customer_ids
        df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce').fillna(pd.Timestamp("1970-01-01"))
        df['order_date'] = df['order_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        df['customer_id'] = df['customer_id'].fillna('GUEST')
        return df
    return apply_clean("orders.csv", "order_id", logic)

def clean_order_items(orders_df):
    def logic(df):
        # Requirement: Referential integrity (drop orphaned items)
        initial_len = len(df)
        df = df[df['order_id'].isin(orders_df['order_id'])]
        print(f"  Dropped {initial_len - len(df)} orphaned records.")
        return df
    return apply_clean("order_items.csv", "item_id", logic)

def main():
    # Execute the full pipeline
    cust_df = clean_customers()
    prod_df = clean_products()
    orders_df = clean_orders()
    clean_order_items(orders_df)
    print("\nAll datasets cleaned successfully and saved to /data/cleaned/")

if __name__ == "__main__":
    main()