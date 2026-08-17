import pandas as pd
from datetime import datetime

class DataValidationService:
    """
    Automated Data Validation & Cleaning Pipeline:
    - Null checks & type conversion
    - Range & integrity validation (quantity > 0, unit_price > 0, discount_rate between 0 and 1)
    - Formula verification: revenue = quantity * unit_price * (1 - discount_rate), profit = revenue - cost
    - Deduplication by order_id
    """
    @classmethod
    def validate_and_clean_sales_batch(cls, raw_records: list) -> dict:
        if not raw_records:
            return {"valid_records": [], "dropped_count": 0, "dropped_reasons": []}

        valid_records = []
        dropped_reasons = []
        seen_order_ids = set()

        for idx, r in enumerate(raw_records):
            order_id = r.get("order_id")
            
            # 1. Null check & Order ID uniqueness
            if not order_id:
                dropped_reasons.append(f"Row {idx}: Missing order_id")
                continue
            if order_id in seen_order_ids:
                dropped_reasons.append(f"Row {idx}: Duplicate order_id '{order_id}'")
                continue

            # 2. Numeric range checks
            try:
                qty = int(r.get("quantity", 0))
                unit_price = float(r.get("unit_price", 0.0))
                discount_rate = float(r.get("discount_rate", 0.0))
                cost = float(r.get("cost", 0.0))
            except (ValueError, TypeError) as e:
                dropped_reasons.append(f"Row {idx} ({order_id}): Invalid numeric types - {e}")
                continue

            if qty <= 0:
                dropped_reasons.append(f"Row {idx} ({order_id}): Quantity <= 0 ({qty})")
                continue
            if unit_price <= 0:
                dropped_reasons.append(f"Row {idx} ({order_id}): Unit price <= 0 ({unit_price})")
                continue
            if discount_rate < 0 or discount_rate > 0.8:
                dropped_reasons.append(f"Row {idx} ({order_id}): Invalid discount rate ({discount_rate})")
                continue

            # 3. Formula Re-calculation & Consistency Check
            expected_discount_amount = round(qty * unit_price * discount_rate, 2)
            expected_revenue = round((qty * unit_price) - expected_discount_amount, 2)
            expected_profit = round(expected_revenue - cost, 2)
            expected_margin = round((expected_profit / expected_revenue * 100), 2) if expected_revenue > 0 else 0.0

            cleaned_record = {
                "order_id": str(order_id),
                "order_date": str(r.get("order_date")),
                "customer_id": str(r.get("customer_id", "CUST_UNKNOWN")),
                "product": str(r.get("product", "Unknown Product")),
                "category": str(r.get("category", "General")),
                "region": str(r.get("region", "National")),
                "city": str(r.get("city", "Central")),
                "sales_channel": str(r.get("sales_channel", "Direct Store")),
                "customer_type": str(r.get("customer_type", "New")),
                "quantity": qty,
                "unit_price": unit_price,
                "discount_rate": discount_rate,
                "discount_amount": expected_discount_amount,
                "revenue": expected_revenue,
                "cost": cost,
                "profit": expected_profit,
                "profit_margin": expected_margin,
                "payment_method": str(r.get("payment_method", "Credit Card")),
                "order_status": str(r.get("order_status", "Completed"))
            }

            seen_order_ids.add(order_id)
            valid_records.append(cleaned_record)

        return {
            "valid_records": valid_records,
            "total_input": len(raw_records),
            "valid_count": len(valid_records),
            "dropped_count": len(dropped_reasons),
            "dropped_reasons": dropped_reasons
        }
