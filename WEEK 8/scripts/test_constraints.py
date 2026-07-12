import sqlite3
import os

DB_PATH = os.path.join("data", "ecommerce_analytics.db")

def test_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print("--- Phase 5: Testing Constraints ---")
    
    # 1. Test Negative Cost Price (Should Fail)
    try:
        cursor.execute("INSERT INTO products (product_id, cost_price) VALUES ('P9999', -100)")
        print("FAIL: Constraint 'cost_price >= 0' not working.")
    except sqlite3.IntegrityError:
        print("SUCCESS: Negative cost price rejected by database.")

    # 2. Test Foreign Key (Should Fail)
    try:
        cursor.execute("INSERT INTO order_items (item_id, order_id) VALUES ('OI999', 'NON-EXISTENT-ID')")
        print("FAIL: Foreign Key constraint not working.")
    except sqlite3.IntegrityError:
        print("SUCCESS: Orphaned order item rejected by database.")
    
    conn.close()

if __name__ == "__main__":
    test_db()
