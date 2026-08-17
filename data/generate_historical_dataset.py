import os
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_historical_sales(days=60, rows_per_day_range=(30, 50), output_path="data/historical_sales.csv"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    end_date = datetime.now() - timedelta(days=1)
    start_date = end_date - timedelta(days=days - 1)
    
    products = [
        {"name": "Laptop Pro", "category": "Electronics", "unit_price": 75000, "cost_pct": 0.65},
        {"name": "Ultra Smartphone", "category": "Electronics", "unit_price": 55000, "cost_pct": 0.60},
        {"name": "4K Monitor 27\"", "category": "Electronics", "unit_price": 28000, "cost_pct": 0.62},
        {"name": "Wireless Noise-Canceling Headphones", "category": "Electronics", "unit_price": 12000, "cost_pct": 0.50},
        {"name": "Mechanical Gaming Keyboard", "category": "Electronics", "unit_price": 6500, "cost_pct": 0.55},
        {"name": "Ergonomic Office Chair", "category": "Furniture", "unit_price": 18000, "cost_pct": 0.58},
        {"name": "Standing Desk", "category": "Furniture", "unit_price": 32000, "cost_pct": 0.64},
        {"name": "USB-C Multiport Dock", "category": "Accessories", "unit_price": 4500, "cost_pct": 0.45},
        {"name": "Smart Fitness Watch", "category": "Accessories", "unit_price": 8500, "cost_pct": 0.52},
        {"name": "Wireless Ergonomic Mouse", "category": "Accessories", "unit_price": 2500, "cost_pct": 0.40}
    ]
    
    regions = [
        {"region": "Maharashtra", "cities": ["Mumbai", "Pune", "Nagpur"], "weight": 0.35},
        {"region": "Gujarat", "cities": ["Ahmedabad", "Surat", "Vadodara"], "weight": 0.20},
        {"region": "Karnataka", "cities": ["Bengaluru", "Mysuru"], "weight": 0.20},
        {"region": "Delhi NCR", "cities": ["New Delhi", "Noida", "Gurugram"], "weight": 0.15},
        {"region": "Tamil Nadu", "cities": ["Chennai", "Coimbatore"], "weight": 0.10}
    ]
    
    channels = ["Online Store", "Retail Outlet", "Direct Sales", "Distributor"]
    payment_methods = ["UPI", "Credit Card", "Net Banking", "Debit Card"]
    
    customers = [f"CUST-{1000 + i}" for i in range(1, 350)]
    
    records = []
    order_counter = 10001
    
    current_date = start_date
    while current_date <= end_date:
        # Introduce weekly fluctuation (higher sales on weekends)
        is_weekend = current_date.weekday() in [5, 6]
        num_orders = random.randint(rows_per_day_range[0], rows_per_day_range[1])
        if is_weekend:
            num_orders = int(num_orders * 1.25)
            
        for _ in range(num_orders):
            prod = random.choice(products)
            reg_info = random.choices(regions, weights=[r["weight"] for r in regions])[0]
            city = random.choice(reg_info["cities"])
            cust = random.choice(customers)
            
            # Customer type (new vs returning)
            is_new = random.random() < 0.35
            cust_type = "New" if is_new else "Returning"
            
            # Timestamp throughout the day
            order_time = current_date + timedelta(
                hours=random.randint(8, 21),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59)
            )
            
            quantity = random.randint(1, 4) if prod["category"] != "Accessories" else random.randint(1, 8)
            unit_price = prod["unit_price"]
            
            # Controlled discount
            discount_rate = round(random.choice([0.0, 0.05, 0.10, 0.15, 0.20]), 2)
            # Occasional flash sale discount
            if random.random() < 0.08:
                discount_rate = 0.25
                
            discount_amount = round(quantity * unit_price * discount_rate, 2)
            revenue = round(quantity * unit_price - discount_amount, 2)
            
            base_cost = quantity * unit_price * prod["cost_pct"]
            cost = round(base_cost * random.uniform(0.96, 1.04), 2)
            profit = round(revenue - cost, 2)
            profit_margin = round((profit / revenue) * 100, 2) if revenue > 0 else 0.0
            
            status = "Completed" if random.random() > 0.03 else "Cancelled"
            
            records.append({
                "order_id": f"ORD-{order_counter}",
                "order_date": order_time.strftime("%Y-%m-%d %H:%M:%S"),
                "customer_id": cust,
                "product": prod["name"],
                "category": prod["category"],
                "region": reg_info["region"],
                "city": city,
                "sales_channel": random.choice(channels),
                "customer_type": cust_type,
                "quantity": quantity,
                "unit_price": unit_price,
                "discount_rate": discount_rate,
                "discount_amount": discount_amount,
                "revenue": revenue,
                "cost": cost,
                "profit": profit,
                "profit_margin": profit_margin,
                "payment_method": random.choice(payment_methods),
                "order_status": status
            })
            order_counter += 1
            
        current_date += timedelta(days=1)
        
    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} historical sales records spanning from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} at {output_path}")

if __name__ == "__main__":
    generate_historical_sales()
