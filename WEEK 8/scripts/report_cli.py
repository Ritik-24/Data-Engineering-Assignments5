import os
import sqlite3
import sys
from datetime import datetime, timedelta

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "ecommerce_analytics.db")
SQL_DIR = os.path.join(BASE_DIR, "sql")

def get_db_connection():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}.")
        sys.exit(1)
    return sqlite3.connect(DB_PATH)

def print_table(headers, rows):
    if not rows:
        print("\n[ Empty Result Set ]\n")
        return
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            val_str = str(val if val is not None else "NULL")
            col_widths[i] = max(col_widths[i], len(val_str))
    format_str = " | ".join([f"{{:<{w}}}" for w in col_widths])
    print("\n" + format_str.format(*headers))
    print("-+-".join(["-" * w for w in col_widths]))
    for row in rows:
        print(format_str.format(*[str(v if v is not None else "NULL") for v in row]))
    print()

def run_dynamic_summary_report(start_date_str, end_date_str):
    # Calculate period delta to fetch comparison data
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.")
        return

    delta = end_date - start_date
    prev_start = (start_date - (delta + timedelta(days=1))).strftime("%Y-%m-%d")
    prev_end = (start_date - timedelta(days=1)).strftime("%Y-%m-%d")

    conn = get_db_connection()
    cursor = conn.cursor()

    def get_metrics(s, e):
        query = """
            SELECT 
                COUNT(DISTINCT o.order_id),
                ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent/100.0)), 2),
                COUNT(DISTINCT o.customer_id)
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE date(o.order_date) BETWEEN date(?) AND date(?);
        """
        cursor.execute(query, (s, e))
        return cursor.fetchone()

    curr = get_metrics(start_date_str, end_date_str)
    prev = get_metrics(prev_start, prev_end)

    print(f"\n--- Period Report: {start_date_str} to {end_date_str} ---")
    headers = ["Metric", "Current", "Previous", "% Change"]
    data = []
    
    # Calculate % changes
    for i in range(3):
        metric_names = ["Orders", "Revenue", "Unique Customers"]
        c, p = curr[i] or 0, prev[i] or 0
        change = ((c - p) / p * 100) if p > 0 else 0
        data.append([metric_names[i], c, p, f"{change:.2f}%"])

    print_table(headers, data)
    
    print("--- Top 3 Products ---")
    cursor.execute("""
        SELECT p.product_name, SUM(oi.quantity) as vol
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        JOIN orders o ON oi.order_id = o.order_id
        WHERE date(o.order_date) BETWEEN date(?) AND date(?)
        GROUP BY p.product_id ORDER BY vol DESC LIMIT 3;
    """, (start_date_str, end_date_str))
    print_table(["Product", "Volume"], cursor.fetchall())
    
    conn.close()

def main():
    if len(sys.argv) < 2:
        print("Usage: python report_cli.py --summary YYYY-MM-DD YYYY-MM-DD OR python report_cli.py --file FILENAME.sql")
        sys.exit(1)
        
    # Handle Summary
    if sys.argv[1] == "--summary":
        start = sys.argv[2] if len(sys.argv) > 2 else "2025-01-01"
        end = sys.argv[3] if len(sys.argv) > 3 else "2026-12-31"
        run_dynamic_summary_report(start, end)
        
    # Handle File Execution
    elif sys.argv[1] == "--file":
        filename = sys.argv[2]
        sql_path = os.path.join(SQL_DIR, filename)
        if not os.path.exists(sql_path):
            print(f"Error: File {filename} not found in {SQL_DIR}")
            return
            
        with open(sql_path, 'r') as f:
            queries = f.read().split(';')
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print(f"\n--- Running: {filename} ---")
        for i, query in enumerate(queries):
            if query.strip():
                print(f"\n>>> Running Query {i+1}")
                cursor.execute(query)
                headers = [description[0] for description in cursor.description]
                print_table(headers, cursor.fetchall())
        conn.close()

if __name__ == "__main__":
    main()