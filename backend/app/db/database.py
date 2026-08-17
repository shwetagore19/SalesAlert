import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_URL = os.getenv("DATABASE_URL", "sqlite:///./sales_intelligence.db")
DATASET_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "historical_sales.csv"))

# For SQLite, check same thread
connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}

engine = create_engine(DB_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from backend.app.db.models import Sale, DailyKPI, AlertRecord, DailyReport
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if sales table has data
        count = db.query(Sale).count()
        if count == 0 and os.path.exists(DATASET_PATH):
            print(f"[DB] Seeding database from historical dataset: {DATASET_PATH}")
            df = pd.read_csv(DATASET_PATH)
            sales_objects = []
            for _, row in df.iterrows():
                sale = Sale(
                    order_id=str(row["order_id"]),
                    order_date=pd.to_datetime(row["order_date"]),
                    customer_id=str(row["customer_id"]),
                    product=str(row["product"]),
                    category=str(row["category"]),
                    region=str(row["region"]),
                    city=str(row["city"]),
                    sales_channel=str(row["sales_channel"]),
                    customer_type=str(row["customer_type"]),
                    quantity=int(row["quantity"]),
                    unit_price=float(row["unit_price"]),
                    discount_rate=float(row["discount_rate"]),
                    discount_amount=float(row["discount_amount"]),
                    revenue=float(row["revenue"]),
                    cost=float(row["cost"]),
                    profit=float(row["profit"]),
                    profit_margin=float(row["profit_margin"]),
                    payment_method=str(row["payment_method"]),
                    order_status=str(row["order_status"])
                )
                sales_objects.append(sale)
            
            db.bulk_save_objects(sales_objects)
            db.commit()
            print(f"[DB] Successfully seeded {len(sales_objects)} sales records into database.")
    except Exception as e:
        print(f"[DB] Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()
