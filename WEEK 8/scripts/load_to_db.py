import os
import sqlite3
import pandas as pd

# Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "ecommerce_analytics.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "sql", "schema.sql")
CLEANED_DIR = os.path.join(BASE_DIR, "data", "cleaned")

def init_db():
    """Initializes the database schema."""
    print("--- Phase 3: Initializing Database Schema ---")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    with open(SCHEMA_PATH, 'r') as f:
        schema_sql = f.read()
    
    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()
    print("Database schema built successfully.")

def load_csv_to_db():
    """Loads cleaned CSVs into the SQLite database."""
    print("\n--- Phase 3: Ingesting Cleaned Datasets ---")
    conn = sqlite3.connect(DB_PATH)
    
    # Order of ingestion is critical for Foreign Key compliance
    datasets = [
        ("customers", "customers_clean.csv"),
        ("products", "products_clean.csv"),
        ("orders", "orders_clean.csv"),
        ("order_items", "order_items_clean.csv")
    ]

    for table_name, csv_file in datasets:
        csv_path = os.path.join(CLEANED_DIR, csv_file)
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            
            # Load into database
            df.to_sql(table_name, conn, if_exists='append', index=False)
            print(f"Loaded {len(df)} rows into table '{table_name}'.")
        else:
            print(f"Error: Clean file {csv_file} not found in {CLEANED_DIR}!")

    conn.close()
    print("\nData migration step completed successfully!")

def main():
    print("E-Commerce Order Analytics System")
    print("Phase 3: Relational DB Migration Setup")
    init_db()
    load_csv_to_db()

if __name__ == "__main__":
    main()