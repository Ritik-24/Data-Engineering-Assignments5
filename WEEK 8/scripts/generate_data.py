import os
import random
import datetime
import pandas as pd
from faker import Faker

# Configuration
fake = Faker("en_IN")
random.seed(42)
Faker.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(RAW_DATA_PATH, exist_ok=True)

# Dataset Sizes
NUM_CUSTOMERS = 500
NUM_PRODUCTS = 500
NUM_ORDERS = 1000
NUM_ORDER_ITEMS = 4000

def _save_to_csv(df, file_name):
    output_file = os.path.join(RAW_DATA_PATH, file_name)
    df.to_csv(output_file, index=False)
    return output_file

def generate_customers():
    customers = []
    for i in range(1, NUM_CUSTOMERS + 1):
        customers.append({
            "customer_id": f"C{i:04}",
            "customer_name": fake.name(),
            "email": fake.email(),
            "registration_date": fake.date_between(start_date="-3y", end_date="today").strftime("%Y-%m-%d"),
            "customer_type": random.choice(["REGULAR", "PREMIUM", "VIP"])
        })
    df = pd.DataFrame(customers)
    
    # Inject exact duplicates
    dup_indices = random.sample(range(len(df)), 50)
    df = pd.concat([df, df.iloc[dup_indices]], ignore_index=True)
    
    _save_to_csv(df, "customers.csv")
    print(f"Generated customers.csv: {len(df)} records.")

def generate_products():
    products = []
    for i in range(1, NUM_PRODUCTS + 1):
        products.append({
            "product_id": f"P{i:04}",
            "product_name": fake.word().capitalize(),
            "category": "Electronics",
            "subcategory": "Mobile",
            "cost_price": round(random.uniform(500, 50000), 2)
        })
    df = pd.DataFrame(products)
    
    # Inject messy names
    for i in range(int(NUM_PRODUCTS * 0.06)): 
        idx = random.randint(0, NUM_PRODUCTS - 1)
        name = df.loc[idx, "product_name"]
        df.loc[idx, "product_name"] = f"  {name}  " if i % 2 == 0 else name.swapcase()
            
    # Inject exact duplicates
    dup_indices = random.sample(range(len(df)), 50)
    df = pd.concat([df, df.iloc[dup_indices]], ignore_index=True)
    
    _save_to_csv(df, "products.csv")
    print(f"Generated products.csv: {len(df)} records.")

def generate_orders():
    orders = []
    for i in range(1, NUM_ORDERS + 1):
        orders.append({
            "order_id": f"O{i:06}",
            "customer_id": f"C{random.randint(1, NUM_CUSTOMERS):04}",
            "order_date": fake.date_time_between(start_date="-2y", end_date="now").strftime("%Y-%m-%d %H:%M:%S"),
            "status": random.choice(["PLACED", "SHIPPED", "DELIVERED", "CANCELLED", "RETURNED"]),
            "region_code": random.choice([101, 102, 103])
        })
    df = pd.DataFrame(orders)
    
    # Inject exact duplicates
    dup_indices = random.sample(range(len(df)), 50)
    df = pd.concat([df, df.iloc[dup_indices]], ignore_index=True)
        
    _save_to_csv(df, "orders.csv")
    print(f"Generated orders.csv: {len(df)} records.")
    return df['order_id'].tolist()

def generate_order_items(valid_order_ids):
    items = []
    for i in range(1, NUM_ORDER_ITEMS + 1):
        items.append({
            "item_id": f"OI{i:06}",
            "order_id": random.choice(valid_order_ids),
            "product_id": f"P{random.randint(1, NUM_PRODUCTS):04}",
            "quantity": random.randint(1, 5),
            "unit_price": round(random.uniform(10, 1000), 2),
            "discount_percent": random.choice([0, 5, 10, 20])
        })
    df = pd.DataFrame(items)
    
    # Inject exact duplicates
    dup_indices = random.sample(range(len(df)), 100)
    df = pd.concat([df, df.iloc[dup_indices]], ignore_index=True)
        
    _save_to_csv(df, "order_items.csv")
    print(f"Generated order_items.csv: {len(df)} records.")

if __name__ == "__main__":
    generate_customers()
    generate_products()
    order_ids = generate_orders()
    generate_order_items(order_ids)