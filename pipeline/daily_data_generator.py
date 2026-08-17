import os
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

DATASET_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "historical_sales.csv"))

class DailyDataGenerator:
    def __init__(self, dataset_path=DATASET_PATH):
        self.dataset_path = dataset_path
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Historical dataset not found at {self.dataset_path}")
        self.df = pd.read_csv(self.dataset_path)

    def generate_day(self, target_date_str=None, num_orders=None):
        """
        Generates daily transaction records for target_date_str preserving realistic business rules.
        """
        self.df = pd.read_csv(self.dataset_path)
        self.df["order_date"] = pd.to_datetime(self.df["order_date"])
        
        last_date = self.df["order_date"].max()
        if target_date_str is None:
            target_date = last_date + timedelta(days=1)
        else:
            target_date = pd.to_datetime(target_date_str)

        # Get last max order_id
        last_id_str = str(self.df["order_id"].max())
        try:
            order_counter = int(last_id_str.replace("ORD-", "")) + 1
        except Exception:
            order_counter = len(self.df) + 10001

        if num_orders is None:
            # Average daily orders with slight variation
            daily_counts = self.df.groupby(self.df["order_date"].dt.date).size()
            avg_count = int(daily_counts.mean()) if len(daily_counts) > 0 else 40
            is_weekend = target_date.weekday() in [5, 6]
            multiplier = 1.2 if is_weekend else random.uniform(0.9, 1.15)
            num_orders = max(15, int(avg_count * multiplier))

        # Products & categories
        products_df = self.df[["product", "category", "unit_price"]].drop_duplicates("product")
        prod_weights = self.df["product"].value_counts(normalize=True).to_dict()
        
        # Region distribution
        regions_df = self.df[["region", "city"]].drop_duplicates()
        region_weights = self.df["region"].value_counts(normalize=True).to_dict()
        
        channels = self.df["sales_channel"].unique().tolist()
        payment_methods = self.df["payment_method"].unique().tolist()
        existing_customers = self.df["customer_id"].unique().tolist()

        new_records = []
        for _ in range(num_orders):
            # Select product
            prod_names = list(prod_weights.keys())
            weights = [prod_weights[p] for p in prod_names]
            p_name = random.choices(prod_names, weights=weights)[0]
            p_row = products_df[products_df["product"] == p_name].iloc[0]
            
            category = p_row["category"]
            unit_price = float(p_row["unit_price"])

            # Region & city
            r_names = list(region_weights.keys())
            r_weights = [region_weights[r] for r in r_names]
            region = random.choices(r_names, weights=r_weights)[0]
            matching_cities = regions_df[regions_df["region"] == region]["city"].tolist()
            city = random.choice(matching_cities) if len(matching_cities) > 0 else "Mumbai"

            # Customer
            if random.random() < 0.35 or len(existing_customers) == 0:
                cust_id = f"CUST-{random.randint(1350, 9999)}"
                cust_type = "New"
            else:
                cust_id = random.choice(existing_customers)
                cust_type = "Returning"

            # Quantity
            quantity = random.randint(1, 4) if category != "Accessories" else random.randint(1, 8)

            # Discount
            discount_rate = round(random.choice([0.0, 0.05, 0.10, 0.15, 0.20]), 2)
            # 5% chance of unusual discount spike
            if random.random() < 0.05:
                discount_rate = random.choice([0.25, 0.30])

            discount_amount = round(quantity * unit_price * discount_rate, 2)
            revenue = round(quantity * unit_price - discount_amount, 2)

            # Cost estimation
            historical_p_data = self.df[self.df["product"] == p_name]
            if len(historical_p_data) > 0:
                avg_cost_ratio = (historical_p_data["cost"] / historical_p_data["revenue"]).mean()
            else:
                avg_cost_ratio = 0.60

            cost = round(revenue * avg_cost_ratio * random.uniform(0.97, 1.03), 2)
            profit = round(revenue - cost, 2)
            profit_margin = round((profit / revenue) * 100, 2) if revenue > 0 else 0.0

            order_time = pd.to_datetime(target_date.strftime("%Y-%m-%d")) + timedelta(
                hours=random.randint(8, 21),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59)
            )

            status = "Completed" if random.random() > 0.04 else "Cancelled"

            new_records.append({
                "order_id": f"ORD-{order_counter}",
                "order_date": order_time.strftime("%Y-%m-%d %H:%M:%S"),
                "customer_id": cust_id,
                "product": p_name,
                "category": category,
                "region": region,
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

        new_df = pd.DataFrame(new_records)
        updated_df = pd.concat([self.df, new_df], ignore_index=True)
        updated_df.to_csv(self.dataset_path, index=False)
        
        total_rev = new_df["revenue"].sum()
        total_prof = new_df["profit"].sum()
        print(f"[DailyGenerator] Successfully generated {len(new_df)} orders for {target_date.strftime('%Y-%m-%d')} (Revenue: Rs. {total_rev:,.2f}, Profit: Rs. {total_prof:,.2f})")
        return {
            "date": target_date.strftime("%Y-%m-%d"),
            "orders_generated": len(new_df),
            "total_revenue": total_rev,
            "total_profit": total_prof,
            "records": new_records
        }

if __name__ == "__main__":
    generator = DailyDataGenerator()
    res = generator.generate_day()
    print("Generation complete:", res["date"], f"({res['orders_generated']} orders)")
